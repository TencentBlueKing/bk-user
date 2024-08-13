# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import datetime
from typing import List

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
            # 注意：更新密码会重置有效期
            if valid_days < 0:
                identify_info.password_expired_at = PERMANENT_TIME
            else:
                identify_info.password_expired_at = timezone.now() + datetime.timedelta(days=valid_days)

            identify_info.save(update_fields=["password", "password_updated_at", "password_expired_at", "updated_at"])

            DataSourceUserDeprecatedPasswordRecord.objects.create(
                user=data_source_user, password=deprecated_password, operator=operator
            )

    @staticmethod
    def batch_update_password(
        data_source_users: List[DataSourceUser],
        password: str,
        valid_days: int,
        operator: str,
    ):
        """
        批量更新用户的密码
        """
        with transaction.atomic():
            identity_info_dict = {
                data_source_user.id: LocalDataSourceIdentityInfo.objects.get(user=data_source_user)
                for data_source_user in data_source_users
            }

            # 批量创建 DataSourceUserDeprecatedPasswordRecord 对象
            DataSourceUserDeprecatedPasswordRecord.objects.bulk_create(
                [
                    DataSourceUserDeprecatedPasswordRecord(
                        user=data_source_user,
                        password=identity_info_dict[data_source_user.id].password,
                        operator=operator,
                    )
                    for data_source_user in data_source_users
                ]
            )

            identify_infos = list(identity_info_dict.values())
            for identify_info in identify_infos:
                identify_info.password = make_password(password)
                identify_info.password_updated_at = timezone.now()
                # 注意：更新密码会重置有效期
                if valid_days < 0:
                    identify_info.password_expired_at = PERMANENT_TIME
                else:
                    identify_info.password_expired_at = timezone.now() + datetime.timedelta(days=valid_days)

            LocalDataSourceIdentityInfo.objects.bulk_update(
                identify_infos, fields=["password", "password_updated_at", "updated_at"]
            )
