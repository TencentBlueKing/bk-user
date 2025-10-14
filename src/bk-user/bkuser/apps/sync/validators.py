# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

# ignore custom logger must use %s string format in this file
# ruff: noqa: G004
from collections import defaultdict

from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.sync.loggers import TaskLogger
from bkuser.apps.tenant.models import TenantUserBuiltinField, TenantUserCustomField


class DataSourceUserFieldUniqueValidator:
    """数据源用户转换器"""

    def __init__(self, data_source: DataSource, logger: TaskLogger):
        self.data_source = data_source
        self.logger = logger
        self.has_duplicate_unique_value = False

    def validate(self):
        # 验证内置字段的唯一性
        self._validate_builtin_fields()

        # 验证自定义字段的唯一性
        self._validate_custom_fields()

        if self.has_duplicate_unique_value:
            raise ValueError("duplicate unique values found")

    def _validate_builtin_fields(self):
        """验证内置字段的唯一性"""
        unique_builtin_fields = TenantUserBuiltinField.objects.filter(
            tenant_id=self.data_source.owner_tenant_id, unique=True
        )

        if not unique_builtin_fields.exists():
            self.logger.info(f"no unique builtin fields found in tenant {self.data_source.owner_tenant_id}")
            return

        # 获取需要验证的字段名列表
        unique_field_names = [f.name for f in unique_builtin_fields]

        # 使用 values 返回字典，便于按字段名访问
        user_builtin_map = DataSourceUser.objects.filter(data_source=self.data_source).values(*unique_field_names)

        for field_config in unique_builtin_fields:
            self.logger.info(f"checking unique builtin field {field_config.display_name}({field_config.name})...")

            # 收集该字段的所有非空值
            counter = defaultdict(list)
            for user_data in user_builtin_map:
                username = user_data["username"]
                field_value = user_data.get(field_config.name)

                # 跳过空值
                if field_value in ["", None]:
                    continue

                counter[field_value].append(username)

            # 检查重复值
            for val, usernames in counter.items():
                if len(usernames) == 1:
                    continue

                self.has_duplicate_unique_value = True
                self.logger.error(
                    (
                        f"builtin field {field_config.display_name}({field_config.name}) "
                        f"has duplicate unique value {val}, usernames: {usernames}"
                    )
                )

    def _validate_custom_fields(self):
        """验证自定义字段的唯一性"""
        unique_custom_fields = TenantUserCustomField.objects.filter(
            tenant_id=self.data_source.owner_tenant_id, unique=True
        )

        if not unique_custom_fields.exists():
            self.logger.info(f"no unique custom fields found in tenant {self.data_source.owner_tenant_id}")
            return

        user_extras_map = dict(
            DataSourceUser.objects.filter(data_source=self.data_source).values_list("username", "extras")
        )

        for f in unique_custom_fields:
            self.logger.info(f"checking unique custom field {f.display_name}({f.name})...")
            counter = defaultdict(list)
            for username, extras in user_extras_map.items():
                # 空值是可以被允许的（非必填字段）
                if f.name in extras and extras[f.name] is not None:
                    counter[extras[f.name]].append(username)

            for val, usernames in counter.items():
                if len(usernames) == 1:
                    continue

                self.has_duplicate_unique_value = True
                self.logger.error(
                    f"custom field {f.display_name}({f.name}) has duplicate unique value {val}, usernames: {usernames}"
                )
