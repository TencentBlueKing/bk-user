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
import base64
import logging
from typing import Dict, Union

from django.conf import settings

from bkuser_core.api.web.constants import EXCLUDE_SETTINGS_META_KEYS
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.error_codes import error_codes
from bkuser_core.departments.models import Department
from bkuser_core.profiles.cache import get_extras_default_from_local_cache
from bkuser_core.profiles.models import DynamicFieldInfo, Profile, ProfileTokenHolder
from bkuser_core.profiles.password import PasswordValidator
from bkuser_core.profiles.utils import check_former_passwords
from bkuser_core.user_settings.exceptions import SettingHasBeenDisabledError
from bkuser_core.user_settings.loader import ConfigProvider
from bkuser_core.user_settings.models import SettingMeta
from bkuser_global.crypt import rsa_decrypt_password

logger = logging.getLogger(__name__)


# FIXME: get it from request.user.username after merge saas into api
def get_operator(request) -> str:
    """
    NOTE: the `operator` should be the username with domain
    - default category: operator = username
    - not default category:  operator = username@domain
    """
    operator = request.META.get(settings.OPERATOR_HEADER, None)
    if not operator:
        raise error_codes.USERNAME_MISSING
    return operator


def get_category_display_name_map() -> Dict[int, str]:
    """
    NOTE: saas 使用, 不加缓存
    """
    return dict(ProfileCategory.objects.values_list("id", "display_name").all())


def get_default_category_id() -> int:
    """
    NOTE: saas 使用, 不加缓存
    """
    return ProfileCategory.objects.get_default().id


def get_department(department_id: int) -> Department:
    try:
        return Department.objects.get(id=department_id)
    except Exception:
        logger.exception("cannot find department: %s", department_id)
        raise error_codes.CANNOT_FIND_DEPARTMENT


def get_category(category_id: int) -> ProfileCategory:
    try:
        return ProfileCategory.objects.get(id=category_id)
    except Exception:
        logger.exception("cannot find category: %s", category_id)
        raise error_codes.CANNOT_FIND_CATEGORY


def get_profile(profile_id: int) -> Profile:
    try:
        return Profile.objects.get(id=profile_id)
    except Exception:
        logger.exception("cannot find profile: %s", profile_id)
        raise error_codes.CANNOT_FIND_PROFILE


def list_setting_metas(category_type: str, region: str, namespace: str) -> list:
    """
    List setting metas.
    """
    queryset = SettingMeta.objects.filter(category_type=category_type).exclude(key__in=EXCLUDE_SETTINGS_META_KEYS)
    if region:
        queryset = queryset.filter(region=region)
    if namespace:
        queryset = queryset.filter(namespace=namespace)
    return queryset.all()


def validate_password(profile: Profile, pending_password: str) -> None:
    config_loader = ConfigProvider(category_id=profile.category_id)
    try:
        max_password_history = config_loader.get("max_password_history", settings.DEFAULT_MAX_PASSWORD_HISTORY)
        if check_former_passwords(profile, pending_password, int(max_password_history)):
            raise error_codes.PASSWORD_DUPLICATED.f(max_password_history=max_password_history)
    except SettingHasBeenDisabledError:
        logger.info("category<%s> has disabled checking password", profile.category_id)

    PasswordValidator(
        min_length=int(config_loader["password_min_length"]),
        max_length=settings.PASSWORD_MAX_LENGTH,
        include_elements=config_loader["password_must_includes"],
        exclude_elements_config=config_loader["exclude_elements_config"],
    ).validate(pending_password)


def is_filter_means_any(ft) -> bool:
    return ft.deconstruct() == ("django.db.models.Q", (("pk__in", []),), {"_negated": True})


def expand_extra_fields(profile: Dict, fields: Dict = None):
    """将 profile extra value 展开，作为 profile 字段展示
    注意当前端传入 ?fields=id,username 时，只会返回这两个字段(在调用点需要处理并传递fields)
    """
    available_values = {}
    if "extras" in profile:
        available_values = profile.pop("extras")

    extras_default = get_extras_default_from_local_cache()
    # TODO: 建模, 建模, 建模
    for key, default in extras_default.items():
        # if ?fields=id,username to control the response fields
        if fields and key not in fields:
            continue

        # 没有设置额外字段，则使用字段默认值
        profile[key] = default
        if not available_values:
            continue

        # 兼容旧的数据格式
        if isinstance(available_values, list):
            available_values = {x["key"]: x["value"] for x in available_values}

        profile[key] = available_values.get(key)

    return profile


def get_extras_with_default_values(extras_from_db: Union[dict, list]) -> dict:
    extras = {}

    # 1. fill the defaults
    # NOTE: 这里供saas使用, 所以不能用cache, 避免变更extra字段后, saas无法感知
    # defaults = get_extras_default_from_local_cache()
    defaults = DynamicFieldInfo.objects.get_extras_default_values()
    extras.update(defaults)

    # 2. fill the values from db
    formatted_extras = extras_from_db
    # 兼容 1.0 存在的旧数据格式(rubbish)
    # [{"is_deleted":false,"name":"\u804c\u7ea7","is_need":false,"is_import_need":true,"value":"",
    # "is_display":true,"is_editable":true,"is_inner":false,"key":"rank","id":9,"is_only":false,
    # "type":"string","order":9}]
    if isinstance(extras_from_db, list):
        formatted_extras = {x["key"]: x["value"] for x in extras_from_db}

    extras.update(formatted_extras)
    return extras


def get_raw_password(category_id: int, encrypted_password: str) -> str:
    config_loader = ConfigProvider(category_id=category_id)
    enable_rsa_encrypted = config_loader.get("enable_password_rsa_encrypted")
    # 未开启，或者未配置rsa
    if not enable_rsa_encrypted:
        return encrypted_password
    rsa_private_key = base64.b64decode(config_loader["password_rsa_private_key"]).decode()
    return rsa_decrypt_password(encrypted_password, rsa_private_key)


def get_token_handler(token: str) -> ProfileTokenHolder:
    try:
        token_holder = ProfileTokenHolder.objects.get(token=token, enabled=True)
    except ProfileTokenHolder.DoesNotExist:
        logger.info("token<%s> not exist in db", token)
        raise error_codes.CANNOT_GET_TOKEN_HOLDER

    if token_holder.expired:
        raise error_codes.PROFILE_TOKEN_EXPIRED

    return token_holder


def get_profile_by_username(username: str, domain: str):
    profile = Profile.objects.filter(username=username, domain=domain)
    if not profile.exists():
        return None
    return profile.first()


def get_profile_by_telephone(telephone: str):
    return Profile.objects.get(telephone=telephone)


def escape_value(input_value: str) -> str:
    """Replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true, the quotation mark character (")
    is also translated.
    rewrite the cgi method
    """
    escaped_value = input_value.replace("&", "")  # Must be done first!
    escaped_value = escaped_value.replace("<", "")
    escaped_value = escaped_value.replace(">", "")
    escaped_value = escaped_value.replace('"', "")
    escaped_value = escaped_value.replace("'", "")
    return escaped_value
