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
from typing import Tuple

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceUser


class CurrentTenantBuiltinDataSourceUserMixin(CurrentUserTenantMixin):
    def get_builtin_data_source_and_user(self) -> Tuple[DataSource, DataSourceUser]:
        """获取内建数据源和用户"""
        # 查询租户的内置管理数据源
        data_source = DataSource.objects.get(
            owner_tenant_id=self.get_current_tenant_id(), type=DataSourceTypeEnum.BUILTIN_MANAGEMENT
        )
        # 查询内置管理账号
        # Note: 理论上没有任何入口可以删除内置管理账号，所以不可能为空
        user = DataSourceUser.objects.get(data_source=data_source)

        return data_source, user
