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
import datetime
import logging
import urllib.parse

from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.celery import app
from bkuser_core.common.notifier import send_mail, send_sms
from bkuser_core.profiles import exceptions
from bkuser_core.profiles.constants import PASSWD_RESET_VIA_SAAS_EMAIL_TMPL
from bkuser_core.profiles.models import Profile
from bkuser_core.profiles.utils import make_passwd_reset_url_by_token
from bkuser_core.user_settings.loader import ConfigProvider
from celery.task import periodic_task
from django.conf import settings
from django.utils.timezone import now

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


class Notification:
    """
    通过 邮件/短信 的方式发送密码过期通知
    """

    def __init__(self, profile):
        self.config_loader = ConfigProvider(profile.category_id)
        self.profile = profile
        self.url = settings.LOGIN_REDIRECT_TO

        valid_period = datetime.timedelta(days=profile.password_valid_days)
        self.expire_at = ((profile.password_update_time or profile.latest_password_update_time) + valid_period) - now()

    def handler(self):

        notice_method_map = {
            "send_email": self._notice_by_email,
            "send_sms": self._notice_by_sms,
        }

        for notice_method in self.config_loader["notice_method"]:
            notice_method_map[notice_method]()

    def _notice_by_email(self):

        if not self.profile.email:
            logger.exception("profiles<%s> has no valid email", self.profile.username)
            raise exceptions.ProfileEmailEmpty

        if (self.expire_at.days < 0) or (self.expire_at.days in self.config_loader["notice_time"]):
            logger.info(
                "--------- going to send notification of password expiration for Profile(%s) via email ----------",
                self.profile.id,
            )

            email_config = (
                self.config_loader["expired_email_config"]
                if self.expire_at.days < 0
                else self.config_loader["expiring_email_config"]
            )

            message = (
                email_config["content"].format(username=self.profile.username, url=self.url)
                if self.expire_at.days < 0
                else email_config["content"].format(
                    username=self.profile.username, expire_at=self.expire_at.days, url=self.url
                )
            )

            send_mail(
                sender=email_config["sender"],
                receivers=[self.profile.email],
                message=message,
                title=email_config["title"],
            )

    def _notice_by_sms(self):

        if not self.profile.telephone:
            logger.exception("profiles<%s> has no valid telephone", self.profile.telephone)
            raise exceptions.ProfileTelephoneEmpty

        if (self.expire_at.days < 0) or (self.expire_at.days in self.config_loader["notice_time"]):
            logger.info(
                "--------- going to send notification of password expiration for Profile(%s) via sms ----------",
                self.profile.id,
            )

            sms_config = (
                self.config_loader["expired_sms_config"]
                if self.expire_at.days < 0
                else self.config_loader["expiring_sms_config"]
            )

            message = (
                sms_config["content"].format(username=self.profile.username, url=self.url)
                if self.expire_at.days < 0
                else sms_config["content"].format(
                    username=self.profile.username, expire_at=self.expire_at.days, url=self.url
                )
            )

            send_sms(receivers=[self.profile.telephone], message=message)


@periodic_task(run_every=30)
def notice_for_password_expiration():
    """密码过期通知"""
    category_ids = ProfileCategory.objects.filter(type=CategoryType.LOCAL.value).values_list("id")
    local_profiles = Profile.objects.filter(category_id__in=category_ids, password_valid_days__gt=0)

    for profile in local_profiles:
        Notification(profile=profile).handler()
