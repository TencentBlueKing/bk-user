# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging
import random
import re
import string
import urllib.parse
from typing import TYPE_CHECKING, Dict, Tuple

from django.conf import settings
from django.contrib.auth.hashers import make_password
from phonenumbers.phonenumberutil import UNKNOWN_REGION, country_code_for_region, region_code_for_country_code

from ..audit.models import ResetPassword
from .exceptions import CountryISOCodeNotMatch, UsernameWithDomainFormatError
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.profiles.validators import DOMAIN_PART_REGEX, USERNAME_REGEX
from bkuser_core.user_settings.constants import InitPasswordMethod
from bkuser_core.user_settings.loader import ConfigProvider
from bkuser_global.local import local
from bkuser_global.utils import force_str_2_bool

if TYPE_CHECKING:
    from bkuser_core.profiles.models import Profile

logger = logging.getLogger(__name__)


def gen_password(length):
    chars = string.ascii_letters + string.digits
    return "".join([random.choice(chars) for _ in range(length)])


USERNAME_DOMAIN_REGEX = re.compile(f"(?P<username>{USERNAME_REGEX})(@(?P<domain>{DOMAIN_PART_REGEX}))?$")


def parse_username_domain(username_with_domain, known_domain: str = None) -> tuple:
    """拆分用户名和登陆域"""

    # 当 domain 已知
    if known_domain:
        if not username_with_domain.endswith(known_domain):
            raise ValueError("known_domain and username_with_domain not matched")

        pattern = re.fullmatch(
            re.compile(f"^(?P<username>{USERNAME_REGEX})(@{known_domain})?"),
            username_with_domain,
        )
        if pattern is None:
            raise UsernameWithDomainFormatError(f"parse {username_with_domain} failed")

        try:
            username = pattern.group("username")
        except AttributeError:
            logger.exception("can not parse raw_username<%s>", username_with_domain)
            raise UsernameWithDomainFormatError(f"parse {username_with_domain} failed")

        logger.debug(
            "parse raw username<%s> to username<%s> & domain<%s>",
            username_with_domain,
            username,
            known_domain,
        )
        return username, known_domain

    pattern = re.fullmatch(USERNAME_DOMAIN_REGEX, username_with_domain)
    if pattern is None:
        raise UsernameWithDomainFormatError(f"parse {username_with_domain} failed")

    try:
        username = pattern.group("username")
        domain = pattern.group("domain")
    except AttributeError:
        logger.exception("parse username with domain fail. [raw_username=%s]", username_with_domain)
        raise UsernameWithDomainFormatError(f"parse {username_with_domain} failed")

    logger.debug(
        "parse raw username<%s> to username<%s> & domain<%s>",
        username_with_domain,
        username,
        domain,
    )
    return username, domain


def make_password_by_config(category_id, return_raw: bool = False) -> Tuple[str, bool]:
    # 目前不支持 API 创建密码
    config_loader = ConfigProvider(category_id=category_id)
    should_notify = False
    if config_loader["init_password_method"] == InitPasswordMethod.FIXED_PRESET.value:
        raw_password = config_loader["init_password"]
    else:
        # 当且仅当自动生成密码时发送邮件
        raw_password = gen_password(8)
        should_notify = True

    if return_raw:
        return raw_password, should_notify

    return make_password(raw_password), should_notify


def align_country_iso_code(country_code: str, iso_code: str) -> Tuple[str, str]:
    """对齐 country code 与 iso code

    iso code 支持大小写输入, 输出大写
    country code 支持数字&字符串输入， 输出字符串
    """

    def _is_unknown_code(country_code: str, iso_code: str):
        return country_code == 0 or iso_code == UNKNOWN_REGION

    if not any([country_code, iso_code]):
        raise ValueError("country code & iso code 不能同时为空")

    if iso_code:
        iso_code = iso_code.upper()

    if all([country_code, iso_code]):
        if not str(country_code_for_region(iso_code)) == country_code:
            raise CountryISOCodeNotMatch

        if _is_unknown_code(country_code, iso_code):
            logger.warning(
                "country code<%s> & iso code<%s> is unknown, return default value instead",
                country_code,
                iso_code,
            )
            return settings.DEFAULT_COUNTRY_CODE, settings.DEFAULT_IOS_CODE

        return str(country_code), iso_code.upper()

    if not country_code:
        country_code = country_code_for_region(iso_code)
    elif not iso_code:
        iso_code = region_code_for_country_code(int(country_code))

    if _is_unknown_code(country_code, iso_code):
        logger.warning(
            "country code<%s> & iso code<%s> is unknown, return default value instead",
            country_code,
            iso_code,
        )
        return settings.DEFAULT_COUNTRY_CODE, settings.DEFAULT_IOS_CODE

    return str(country_code), iso_code.upper()


def force_use_raw_username(request):
    """判断是否强制使用原生 username"""
    if not request:
        return True

    if settings.FORCE_RAW_USERNAME_HEADER in request.META:
        return force_str_2_bool(request.META[settings.FORCE_RAW_USERNAME_HEADER])

    return False


def get_username(force_use_raw: bool, category_id: int, username: str, domain: str):
    """获取用户名(通过请求头返回 username 形式)"""

    if force_use_raw:
        return username

    if ProfileCategory.objects.get_default().id == category_id:
        return username
    else:
        return f"{username}@{domain}"


def check_former_passwords(
    instance: "Profile",
    new_password: str,
    max_history: int = settings.DEFAULT_MAX_PASSWORD_HISTORY,
) -> bool:
    """Check if new password in last passwords"""
    reset_records = ResetPassword.objects.filter(profile=instance).order_by("-create_time")[:max_history]
    former_passwords = [x.password for x in reset_records]

    return new_password in former_passwords


def make_passwd_reset_url_by_token(token: str):
    """make reset"""
    return urllib.parse.urljoin(settings.SAAS_URL, f"set_password?token={token}")


def _get_bk_app_code_from_request(request) -> str:
    """if the requests are from apigateway"""
    return getattr(request, "bk_app_code", "")


def _get_bk_app_code_from_request_param(request) -> str:
    """currently, some env can't get the bk_app_code from request, so we use the param to get it
    FIXME: will remove later after the inner env esb change from token to jwt
    """
    if not request:
        return ""
    return request.GET.get("app_id", "")


def _is_saas_request(request) -> bool:
    """if the request is from saas"""
    if not request:
        return False

    return local.request_username == "SAAS"


def remove_sensitive_fields_for_profile(request, data: Dict) -> Dict:
    """remove sensitive fields for profile"""
    if not settings.ENABLE_PROFILE_SENSITIVE_FILTER:
        return data

    # if no request or no data, return
    if not (request and data):
        return data

    # if from saas, return
    if _is_saas_request(request):
        return data

    # FIXME: currently get from request_param,
    # will change to get from request after the inner env esb change from token to jwt
    bk_app_code = _get_bk_app_code_from_request_param(request)

    # remove sensitive fields, except the app_code in whitelist
    for key in settings.PROFILE_SENSITIVE_FIELDS:
        if key in data and bk_app_code not in settings.PROFILE_SENSITIVE_FIELDS_WHITELIST_APP_CODES:
            data[key] = ""
            # data.pop(key)

    # remove sensitive extras fields, except the app_code in whitelist
    if "extras" in data:
        extras = data["extras"]
        for key in settings.PROFILE_EXTRAS_SENSITIVE_FIELDS:
            if key in extras and bk_app_code not in settings.PROFILE_EXTRAS_SENSITIVE_FIELDS_WHITELIST_APP_CODES:
                extras.pop(key)

    return data
