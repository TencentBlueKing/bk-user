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
import datetime,time
import logging

from django.db.models import Exists, OuterRef

from bkuser_core.audit.models import LogIn
from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.profiles.constants import NOTICE_METHOD_EMAIL, NOTICE_METHOD_SMS
from bkuser_core.profiles.models import Profile
from bkuser_core.user_settings.constants import PASSWORD_EXPIRATION_NOTICE_INTERVAL_META_KEY, SettingsEnableNamespaces
from bkuser_core.user_settings.loader import ConfigProvider
from bkuser_core.user_settings.models import Setting

logger = logging.getLogger(__name__)


def get_profiles_for_password_expiration():
    """
    获取 需要进行密码过期相关通知的用户
    """
    expiring_profile_list = []
    expired_profile_list = []
    category_ids = ProfileCategory.objects.filter(type=CategoryType.LOCAL.value).values_list("id", flat=True)
    logined_profiles = get_logined_profiles()

    for category_id in category_ids:
        notice_interval = Setting.objects.filter(
                category_id=category_id,
                meta__key=PASSWORD_EXPIRATION_NOTICE_INTERVAL_META_KEY,
                meta__namespace=SettingsEnableNamespaces.PASSWORD.value,
            ).first().value
        expire_profiles = logined_profiles.objects.filter(category_id=category_id, password_valid_days__gt=0).values("id", "username", "category_id", "email", "telephone", "password_valid_days","password_update_time",
                "create_time")
        expiration_times = get_expiration_dates(notice_interval)
        for profile in expire_profiles:
            valid_period = datetime.timedelta(days=profile["password_valid_days"])
            expire_at = (profile["password_update_time"] or profile["create_time"]) + valid_period
            if expire_at.date() in expiration_times:
                expiring_profile_list.append(profile)
            if expire_at.date() < datetime.date.today():
                expired_profile_list.append(profile)
    return expiring_profile_list, expired_profile_list


def get_expiration_dates(notice_interval):
    """
    获取需要进行通知的 过期时间列表
    """
    expiration_times = []
    for t in notice_interval:
        expiration_time = datetime.date.today() + datetime.timedelta(days=t)
        expiration_times.append(expiration_time)

    return expiration_times


def get_notice_config_for_password_expiration(profile):
    """
    整合 密码过期 通知内容
    """
    notice_config = {}
    expire_at = (
        (profile["password_update_time"].date() or profile["create_time"].date())
        + datetime.timedelta(days=profile["password_valid_days"])
        - datetime.date.today()
    )

    config_loader = ConfigProvider(profile["category_id"])
    notice_methods = config_loader["password_expiration_notice_methods"]

    if not notice_methods:
        return

    if NOTICE_METHOD_EMAIL in notice_methods:
        email_config = (
            config_loader["expired_password_email_config"]
            if expire_at.days < 0
            else config_loader["expiring_password_email_config"]
        )

        message = (
            email_config["content"].format(username=profile["username"],url="")
            if expire_at.days < 0
            else email_config["content"].format(username=profile["username"], expire_at=expire_at.days,url="")
        )

        notice_config.update(
            {
                "send_email": {
                    "sender": email_config["sender"],
                    "receivers": [profile["email"]],
                    "message": message,
                    "title": email_config["title"],
                }
            }
        )

    if NOTICE_METHOD_SMS in notice_methods:
        sms_config = (
            config_loader["expired_password_sms_config"]
            if expire_at.days < 0
            else config_loader["expiring_password_sms_config"]
        )

        message = (
            sms_config["content"].format(username=profile["username"])
            if expire_at.days < 0
            else sms_config["content"].format(username=profile["username"], expire_at=expire_at.days)
        )

        notice_config.update(
            {"send_sms": {"sender": sms_config["sender"], "receivers": [profile["telephone"]], "message": message}}
        )

    return notice_config


def get_logined_profiles():
    """
    获取在平台登录过的所有用户
    """
    subquery = LogIn.objects.filter(profile=OuterRef('pk')).values_list('id')
    logined_profile_ids = (
        Profile.objects.annotate(temp=Exists(subquery)).filter(temp=True).values_list('id', flat=True)
    )
    logined_profiles = Profile.objects.filter(id__in=logined_profile_ids)

    return logined_profiles
