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

from django.db.models import Exists, OuterRef

from bkuser_core.audit.models import LogIn
from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.notifier import send_mail, send_sms
from bkuser_core.profiles.constants import NOTICE_METHOD_EMAIL, NOTICE_METHOD_SMS, TypeOfExpiration
from bkuser_core.profiles.models import Profile
from bkuser_core.user_settings.constants import (
    ACCOUNT_EXPIRATION_NOTICE_INTERVAL_META_KEY,
    PASSWORD_EXPIRATION_NOTICE_INTERVAL_META_KEY,
    SettingsEnableNamespaces,
)
from bkuser_core.user_settings.loader import ConfigProvider
from bkuser_core.user_settings.models import Setting

logger = logging.getLogger(__name__)


class ExpirationNotifier:
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
        send_sms(sender=sms_config["sender"], receivers=sms_config["receivers"], message=sms_config["message"])


def get_logined_profiles():
    """
    获取在平台登录过的所有用户
    """
    subquery = LogIn.objects.filter(profile=OuterRef("pk")).values_list("id")
    logined_profile_ids = (
        Profile.objects.annotate(temp=Exists(subquery)).filter(temp=True).values_list("id", flat=True)
    )
    logined_profiles = Profile.objects.filter(id__in=logined_profile_ids)

    return logined_profiles


def get_expiration_dates(notice_interval):
    """
    获取需要进行通知的 过期时间列表
    """
    expiration_dates = []
    for day in notice_interval:
        expiration_date = datetime.date.today() + datetime.timedelta(days=day)
        expiration_dates.append(expiration_date)

    return expiration_dates


# pylint: disable=function-name-too-long
def get_config_from_all_local_categories():
    """一次性拉取所有目录的ConfigProvider"""
    category_config_map = {}
    category_ids = ProfileCategory.objects.filter(type=CategoryType.LOCAL.value).values_list("id", flat=True)

    for category_id in category_ids:
        config_loader = ConfigProvider(category_id)
        category_config_map[category_id] = config_loader

    return category_config_map


def get_notice_config_for_expiration(expiration_type, profile, config_loader):
    """
    整合 过期 通知内容
    """
    notice_config = {}

    if expiration_type == TypeOfExpiration.ACCOUNT_EXPIRATION.value:
        logger.info("--------- get notice config for account expiration ----------")
        notice_methods = config_loader["account_expiration_notice_methods"]
        expired_at = profile["account_expiration_date"] - datetime.date.today()
        expired_email_config = config_loader["expired_account_email_config"]
        expiring_email_config = config_loader["expiring_account_email_config"]
        expired_sms_config = config_loader["expired_account_sms_config"]
        expiring_sms_config = config_loader["expiring_account_sms_config"]

    elif expiration_type == TypeOfExpiration.PASSWORD_EXPIRATION.value:
        logger.info("--------- get notice config for password expiration ----------")
        notice_methods = config_loader["password_expiration_notice_methods"]
        expired_at = (
            (profile["password_update_time"].date() or profile["create_time"].date())
            + datetime.timedelta(days=profile["password_valid_days"])
            - datetime.date.today()
        )
        expired_email_config = config_loader["expired_password_email_config"]
        expiring_email_config = config_loader["expiring_password_email_config"]
        expired_sms_config = config_loader["expired_password_sms_config"]
        expiring_sms_config = config_loader["expiring_password_sms_config"]

    if not notice_methods:
        return

    if NOTICE_METHOD_EMAIL in notice_methods:
        email_config = expired_email_config if expired_at.days < 0 else expiring_email_config

        message = (
            email_config["content"].format(username=profile["username"])
            if expired_at.days < 0
            else email_config["content"].format(username=profile["username"], expired_at=expired_at.days)
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
        sms_config = expired_sms_config if expired_at.days < 0 else expiring_sms_config

        message = (
            sms_config["content"].format(username=profile["username"])
            if expired_at.days < 0
            else sms_config["content"].format(username=profile["username"], expired_at=expired_at.days)
        )

        notice_config.update(
            {"send_sms": {"sender": sms_config["sender"], "receivers": [profile["telephone"]], "message": message}}
        )
    logger.debug("--------- notice_config(%s) of profile(%s) ----------", notice_config, profile)

    return notice_config


def get_profiles_for_account_expiration():
    """
    获取 需要进行账号过期相关通知的用户
    """
    expiring_profile_list = []
    expired_profile_list = []
    category_ids = ProfileCategory.objects.filter(type=CategoryType.LOCAL.value).values_list("id", flat=True)

    for category_id in category_ids:
        notice_interval = (
            Setting.objects.filter(
                category_id=category_id,
                meta__key=ACCOUNT_EXPIRATION_NOTICE_INTERVAL_META_KEY,
                meta__namespace=SettingsEnableNamespaces.ACCOUNT.value,
            )
            .first()
            .value
        )

        expiration_dates = get_expiration_dates(notice_interval)
        logined_profiles = get_logined_profiles()

        expiring_profiles = logined_profiles.filter(
            account_expiration_date__in=expiration_dates, category_id=category_id
        ).values("id", "username", "category_id", "email", "telephone", "account_expiration_date")
        expiring_profile_list.extend(expiring_profiles)

        expired_profiles = logined_profiles.filter(
            account_expiration_date__lt=datetime.date.today(), category_id=category_id
        ).values("id", "username", "category_id", "email", "telephone", "account_expiration_date")
        expired_profile_list.extend(expired_profiles)

    return expiring_profile_list, expired_profile_list


# pylint: disable=function-name-too-long
def get_profiles_for_password_expiration():
    """
    获取 需要进行密码过期相关通知的用户
    """
    expiring_profile_list = []
    expired_profile_list = []
    category_ids = ProfileCategory.objects.filter(type=CategoryType.LOCAL.value).values_list("id", flat=True)
    logined_profiles = get_logined_profiles()

    for category_id in category_ids:
        notice_interval = (
            Setting.objects.filter(
                category_id=category_id,
                meta__key=PASSWORD_EXPIRATION_NOTICE_INTERVAL_META_KEY,
                meta__namespace=SettingsEnableNamespaces.PASSWORD.value,
            )
            .first()
            .value
        )

        expiration_dates = get_expiration_dates(notice_interval)
        profiles = logined_profiles.filter(category_id=category_id, password_valid_days__gt=0).values(
            "id",
            "username",
            "category_id",
            "email",
            "telephone",
            "password_valid_days",
            "password_update_time",
            "create_time",
        )
        for profile in profiles:
            valid_period = datetime.timedelta(days=profile["password_valid_days"])
            expired_at = (profile["password_update_time"] or profile["create_time"]) + valid_period

            if expired_at.date() in expiration_dates:
                expiring_profile_list.append(profile)

            if expired_at.date() < datetime.date.today():
                expired_profile_list.append(profile)

    return expiring_profile_list, expired_profile_list
