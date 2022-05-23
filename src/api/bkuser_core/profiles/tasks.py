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
import time
import urllib.parse

from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings

from .account_expiration_notifier import (
    AccountExpirationNotifier,
    get_notice_config_for_account_expiration,
    get_profiles_for_account_expiration,
)
from bkuser_core.celery import app
from bkuser_core.common.notifier import send_mail
from bkuser_core.profiles import exceptions
from bkuser_core.profiles.constants import PASSWD_RESET_VIA_SAAS_EMAIL_TMPL
from bkuser_core.profiles.models import AccountExpirationNoticeRecord, Profile
from bkuser_core.profiles.utils import make_passwd_reset_url_by_token
from bkuser_core.user_settings.loader import ConfigProvider

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


@periodic_task(run_every=crontab(minute='0', hour='2'))
def notice_for_account_expiration():
    """
    用户账号过期通知
    """
    expiring_profile_list, expired_profile_list = get_profiles_for_account_expiration()

    for profile in expiring_profile_list:
        notice_config = get_notice_config_for_account_expiration(profile)
        if not notice_config:
            return
        AccountExpirationNotifier().handler(notice_config)
        time.sleep(settings.NOTICE_INTERVAL_SECONDS)

    for profile in expired_profile_list:
        notice_config = get_notice_config_for_account_expiration(profile)
        if not notice_config:
            return
        notice_record = AccountExpirationNoticeRecord.objects.filter(profile_id=profile.id)

        if not notice_record:
            AccountExpirationNotifier().handler(notice_config)
            AccountExpirationNoticeRecord.objects.create(notice_date=datetime.date.today(), profile_id=profile.id)
            time.sleep(settings.NOTICE_INTERVAL_SECONDS)
            return

        # 上一次过期通知的时间距离现在超过一个月则进行通知
        if notice_record.notice_date < datetime.date.today() - datetime.timedelta(days=30):
            AccountExpirationNotifier().handler(notice_config)
            notice_record.objects.update(notice_date=datetime.date.today())
            time.sleep(settings.NOTICE_INTERVAL_SECONDS)
            return
