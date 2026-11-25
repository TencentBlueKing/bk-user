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

# ignore custom logger must use %s string format in this file
# ruff: noqa: G004
from typing import List

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.data_source.transform import UsernameTransformer
from bkuser.apps.sync.contexts import DataSourceSyncTaskContext
from bkuser.plugins.models import RawDataSourceUser


class CrossDataSourceUsernameConflictExcluder:
    """排除与同租户下其他数据源存在用户名冲突的用户"""

    def __init__(self, ctx: DataSourceSyncTaskContext, data_source: DataSource):
        self.ctx = ctx
        self.data_source = data_source
        self.transformer = UsernameTransformer.load(data_source.id)

    def exclude(self, raw_users: List[RawDataSourceUser]) -> List[RawDataSourceUser]:
        if not raw_users:
            return raw_users

        code_username_map = {user.code: self.transformer.to_stored(user.properties["username"]) for user in raw_users}

        # 查询同租户下其他数据源中已存在的冲突用户名
        conflict_usernames = set(
            DataSourceUser.objects.filter(
                data_source__owner_tenant_id=self.data_source.owner_tenant_id,
                data_source__type=DataSourceTypeEnum.REAL,
                username__in=code_username_map.values(),
            )
            .exclude(data_source=self.data_source)
            .values_list("username", flat=True)
        )

        if not conflict_usernames:
            return raw_users

        filtered_users, skipped_usernames = [], []
        for user in raw_users:
            if code_username_map[user.code] in conflict_usernames:
                skipped_usernames.append(code_username_map[user.code])
            else:
                filtered_users.append(user)

        self.ctx.logger.warning(
            f"skip {len(skipped_usernames)} users whose username already exists in other data sources "
            f"of the same tenant: {', '.join(skipped_usernames)}"
        )

        return filtered_users
