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
import urllib.parse

from django.conf import settings

from bkuser_core.celery import app
from bkuser_core.common.notifier import send_mail, send_sms
from bkuser_core.profiles import exceptions
from bkuser_core.profiles.constants import PASSWD_RESET_VIA_SAAS_EMAIL_TMPL
from bkuser_core.profiles.models import Profile
from bkuser_core.profiles.utils import make_passwd_reset_url_by_token
from bkuser_core.user_settings.loader import ConfigProvider, GlobalConfigProvider

logger = logging.getLogger(__name__)


@app.task
def send_password_by_email(profile_id: int, raw_password: str = None, init: bool = True, token: str = None):
    """发送密码到邮箱，支持初始化 & 重置"""
    logger.info(
        "--------- going to send password of Profile(%s) via email ----------",
        profile_id,
    )
    try:
        profile = Profile.objects.get(id=profile_id)
    except Exception:
        logger.exception("get profile<id=%s> failed during send mail", profile_id)
        raise

    if not profile.email:
        logger.exception("profiles<username=%s> has no valid email", profile.username)
        raise exceptions.ProfileEmailEmpty

    config_loader = ConfigProvider(profile.category_id)

    if init:
        email_config = config_loader["init_mail_config"]
        url = settings.LOGIN_REDIRECT_TO
        message = email_config["content"].format(username=profile.username, password=raw_password, url=url)
    else:
        # 从平台重置密码
        if token:
            email_config = config_loader["reset_mail_config"]
            message = email_config["content"].format(
                url=make_passwd_reset_url_by_token(token),
                reset_url=urllib.parse.urljoin(settings.SAAS_URL, "reset_password"),
            )
        # 在用户管理里管理操作重置密码
        else:
            email_config = config_loader["reset_mail_config"]
            message = PASSWD_RESET_VIA_SAAS_EMAIL_TMPL.format(username=profile.username)

    send_mail(
        sender=email_config["sender"],
        receivers=[profile.email],
        message=message,
        title=email_config["title"],
    )


@app.task
def send_captcha(send_data_struct):
    profile = Profile.objects.get(id=send_data_struct.pop("profile"))
    config_loader = GlobalConfigProvider(send_data_struct["authentication_type"])

    if config_loader.get("send_method") == "email":
        email_config = config_loader.get("email_config")
        message = email_config["content"].format(
            captcha=send_data_struct["captcha"], expire_seconds=int(send_data_struct["expire_seconds"] / 60)
        )
        logger.info(
            "--------- going to send captcha of Profile(%s) via email ----------",
            profile.id,
        )
        send_mail(
            sender=email_config["sender"],
            receivers=[send_data_struct["authenticated_value"]],
            message=message,
            title=email_config["title"],
        )
    elif config_loader.get("send_method") == "telephone":
        logger.info(
            "--------- going to send captcha of Profile(%s) via telephone ----------",
            profile.id,
        )
        sms_config = config_loader.get("sms_config")
        message = sms_config["content"].format(
            captcha=send_data_struct["captcha"], expire_seconds=int(send_data_struct["expire_seconds"] / 60)
        )
        logger.info(
            "--------- going to send captcha of Profile(%s) via email ----------",
            profile.id,
        )
        send_sms(
            sender=sms_config["sender"],
            receivers=[send_data_struct["authenticated_value"]],
            message=message,
        )
