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
from bkuser_core.user_settings.constants import ACCOUNT_EXPIRATION_NOTICE_INTERVAL_META_KEY, SettingsEnableNamespaces
from bkuser_core.user_settings.models import Setting

logger = logging.getLogger(__name__)


def get_profiles_for_account_expiration():
    """
    获取 需要进行账号过期相关通知的用户
    """
    expiring_profile_list = []
    expired_profile_list = []
    category_ids = ProfileCategory.objects.filter(type=CategoryType.LOCAL.value).values_list("id", flat=True)

    for category_id in category_ids:
        notice_interval = Setting.objects.filter(
            category_id=category_id,
            meta__key=ACCOUNT_EXPIRATION_NOTICE_INTERVAL_META_KEY,
            meta__namespace=SettingsEnableNamespaces.ACCOUNT.value
        ).first().value

        expiration_dates = get_expiration_dates(notice_interval)
        logined_profiles = get_logined_profiles()

        expiring_profiles = logined_profiles.filter(
            account_expiration_date__in=expiration_dates,
            category_id=category_id).values(
            "id", "username", "category_id", "email", "telephone", "account_expiration_date")
        expiring_profile_list.extend(expiring_profiles)

        expired_profiles = logined_profiles.filter(
            account_expiration_date__lt=datetime.date.today(),
            category_id=category_id).values(
            "id", "username", "category_id", "email", "telephone", "account_expiration_date")
        expired_profile_list.extend(expired_profiles)

    return expiring_profile_list, expired_profile_list
