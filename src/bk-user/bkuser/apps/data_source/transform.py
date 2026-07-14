# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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

from bkuser.apps.data_source.models import DataSourceUsernameGenerateConfig


class UsernameTransformer:
    """用户名转换器，负责原始用户名与存储用户名之间的转换"""

    def __init__(self, prefix: str = "", suffix: str = ""):
        self.prefix = prefix
        self.suffix = suffix
        self.unchanged = not prefix and not suffix

    def to_stored(self, raw_username: str) -> str:
        """原始用户名 → 存储用户名"""
        if self.unchanged:
            return raw_username

        return f"{self.prefix}{raw_username}{self.suffix}"

    def to_raw(self, stored_username: str) -> str:
        """存储用户名 → 原始用户名"""
        if self.unchanged:
            return stored_username

        result = stored_username
        if self.prefix and result.startswith(self.prefix):
            result = result[len(self.prefix) :]

        if self.suffix and result.endswith(self.suffix):
            result = result[: -len(self.suffix)]

        return result

    @classmethod
    def load(cls, data_source_id: int) -> "UsernameTransformer":
        """加载指定数据源的用户名转换器"""
        row = (
            DataSourceUsernameGenerateConfig.objects.filter(data_source_id=data_source_id)
            .values_list("prefix", "suffix")
            .first()
        )

        if row is None:
            return cls()

        return cls(prefix=row[0], suffix=row[1])
