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

from bkuser_core.audit.models import LogIn
from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.celery import app
from bkuser_core.common.notifier import send_mail, send_sms
from bkuser_core.profiles import exceptions
from bkuser_core.profiles.constants import PASSWD_RESET_VIA_SAAS_EMAIL_TMPL
from bkuser_core.profiles.models import Profile
from bkuser_core.profiles.utils import make_passwd_reset_url_by_token
from bkuser_core.user_settings.constants import SettingsEnableNamespaces
from bkuser_core.user_settings.loader import ConfigProvider
from bkuser_core.user_settings.models import Setting
from celery.task import periodic_task
from django.conf import settings
from django.db.models import Exists, OuterRef, Q

logger = logging.getLogger(__name__)

EMAIL_NOTICE_METHOD = "send_email"
SMS_NOTICE_METHOD = "send_sms"


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


def get_profiles_for_account_expiration():
    """
    获取 需要进行账号过期相关通知的用户
    """

    profiles = []
    category_ids = ProfileCategory.objects.filter(type=CategoryType.LOCAL.value).values_list("id", flat=True)

    for category_id in category_ids:
        notice_times = Setting.objects.filter(
            category_id=category_id,
            meta__key="account_expiration_notice_times",
            meta__namespace=SettingsEnableNamespaces.ACCOUNT.value
        ).first().value

        expiration_times = get_expiration_times(notice_times)
        logined_profiles = get_logined_profiles()

        expiring_profiles = logined_profiles.filter(
            Q(account_expiration_time__lt=datetime.date.today()) |
            Q(account_expiration_time__in=expiration_times),
            category_id=category_id)
        profiles.extend(expiring_profiles)

    return profiles


def get_expiration_times(notice_times):
    """
    获取需要进行通知的 过期时间列表
    """
    expiration_times = []
    for t in notice_times:
        expiration_time = datetime.date.today() + datetime.timedelta(days=t)
        expiration_times.append(expiration_time)

    return expiration_times


def get_logined_profiles():
    """
    获取在平台登录过的所有用户
    """
    subquery = LogIn.objects.filter(profile=OuterRef('pk')).values_list('id')
    logined_profile_ids = Profile.objects.annotate(
        temp=Exists(subquery)).filter(temp=True).values_list('id', flat=True)
    logined_profiles = Profile.objects.filter(id__in=logined_profile_ids)

    return logined_profiles


def get_notice_config_for_account_expiration(profile):
    """
    整合 账号过期 通知内容
    """
    notice_config = {}
    expire_at = datetime.date.today() - profile.account_expiration_time

    config_loader = ConfigProvider(profile.category_id)
    notice_methods = config_loader["account_expiration_notice_methods"]

    if EMAIL_NOTICE_METHOD in notice_methods:
        email_config = (
            config_loader["expired_account_email_config"]
            if expire_at.days < 0
            else config_loader["expiring_account_email_config"]
        )

        message = (
            email_config["content"].format(username=profile.username)
            if expire_at.days < 0
            else email_config["content"].format(
                username=profile.username, expire_at=expire_at.days
            )
        )

        notice_config.update(
            {
                "send_email":
                    {
                        "sender": email_config["sender"],
                        "receiver": [profile.email],
                        "message": message,
                        "title": email_config["title"]
                    }

            }
        )

    if SMS_NOTICE_METHOD in notice_methods:
        sms_config = (
            config_loader["expired_account_sms_config"]
            if expire_at.days < 0
            else config_loader["expiring_account_sms_config"]
        )

        message = (
            sms_config["content"].format(username=profile.username)
            if expire_at.days < 0
            else sms_config["content"].format(
                username=profile.username, expire_at=expire_at.days
            )
        )

        notice_config.update(
            {
                "send_sms":
                    {
                        "receivers": [profile.telephone],
                        "message": message
                    }

            }
        )

    return notice_config


class Notifier:
    def handler(self, notice_config):

        notice_method_map = {
            "send_email": self._notice_by_email,
            "send_sms": self._notice_by_sms,
        }

        for notice_method in notice_config:
            notice_method_map[notice_method](notice_config[notice_method])

    def _notice_by_email(self, email_config):
        send_mail(
            sender=email_config["sender"],
            receivers=email_config["receivers"],
            message=email_config["message"],
            title=email_config["title"],
        )

    def _notice_by_sms(self, sms_config):
        send_sms(
            sender=sms_config["sender"],
            receivers=sms_config["receivers"],
            message=sms_config["message"]
        )


@periodic_task(run_every=48000)
def notice_for_account_expiration():
    """
    用户账号过期通知
    """
    profiles = get_profiles_for_account_expiration()

    for profile in profiles:
        notice_config = get_notice_config_for_account_expiration(profile)
        Notifier().handler(notice_config)
