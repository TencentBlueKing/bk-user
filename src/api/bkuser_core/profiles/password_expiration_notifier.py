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

from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.profiles.notifier import get_expiration_dates, get_logined_profiles
from bkuser_core.user_settings.constants import PASSWORD_EXPIRATION_NOTICE_INTERVAL_META_KEY, SettingsEnableNamespaces
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
