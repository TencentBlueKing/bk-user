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

from django.db import transaction
from django.utils import timezone

from bkuser.apps.data_source.models import (
    DataSourceUser,
    DataSourceUserDeprecatedPasswordRecord,
    LocalDataSourceIdentityInfo,
)
from bkuser.common.constants import PERMANENT_TIME
from bkuser.common.hashers import make_password


class DataSourceUserHandler:
    @staticmethod
    def update_password(
        data_source_user: DataSourceUser,
        password: str,
        valid_days: int,
        operator: str,
    ):
        """
        更新某个用户的密码
        """
        identify_info = LocalDataSourceIdentityInfo.objects.get(user=data_source_user)
        deprecated_password = identify_info.password

        with transaction.atomic():
            identify_info.password = make_password(password)
            identify_info.password_updated_at = timezone.now()
            if valid_days < 0:
                identify_info.password_expired_at = PERMANENT_TIME
            else:
                identify_info.password_expired_at = timezone.now() + datetime.timedelta(days=valid_days)

            identify_info.save(update_fields=["password", "password_updated_at", "password_expired_at", "updated_at"])

            DataSourceUserDeprecatedPasswordRecord.objects.create(
                user=data_source_user, password=deprecated_password, operator=operator
            )
