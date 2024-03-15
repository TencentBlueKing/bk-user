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
from typing import List

from pydantic import BaseModel

from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourcePlugin,
    DataSourceSensitiveInfo,
    DataSourceUser,
    DataSourceUserLeaderRelation,
    DepartmentRelationMPTTTree,
)
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.plugins.base import get_default_plugin_cfg
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig, PasswordInitialConfig


class DataSourceSimpleInfo(BaseModel):
    id: int
    name: str


class DataSourceHandler:
    @staticmethod
    def create_local_data_source_with_merge_config(
        data_source_name: str,
        owner_tenant_id: str,
        password_initial_config: PasswordInitialConfig,
    ) -> DataSource:
        """使用与默认配置合并后的插件配置，创建本地数据源"""
        plugin_id = DataSourcePluginEnum.LOCAL
        plugin_config: LocalDataSourcePluginConfig = get_default_plugin_cfg(plugin_id)  # type: ignore
        plugin_config.password_initial = password_initial_config

        return DataSource.objects.create(
            name=data_source_name,
            owner_tenant_id=owner_tenant_id,
            plugin=DataSourcePlugin.objects.get(id=plugin_id),
            plugin_config=plugin_config,
        )

    @staticmethod
    def get_tenant_available_data_sources(tenant_id: str) -> List[DataSource]:
        """获取租户能查看的数据源，包括拥有的以及协同的"""
        # TODO (su) 考虑租户协同的情况
        return DataSource.objects.filter(owner_tenant_id=tenant_id)

    @staticmethod
    def delete_data_source_and_related_resources(data_source: DataSource) -> None:
        """重要：必须在事务内调用该方法"""

        # ======== 删除租户相关模型数据 ========
        # 1. 删除租户部门数据
        TenantDepartment.objects.filter(data_source=data_source).delete()
        # 2. 删除租户用户数据
        TenantUser.objects.filter(data_source=data_source).delete()

        # ======== 删除数据源相关模型数据 ========
        # 1. 删除部门 - 用户关系
        DataSourceDepartmentUserRelation.objects.filter(data_source=data_source).delete()
        # 2. 删除部门 - 部门关系
        DataSourceDepartmentRelation.objects.filter(data_source=data_source).delete()
        # 3. 删除数据源部门
        DataSourceDepartment.objects.filter(data_source=data_source).delete()
        # 4. 删除 Leader - 用户关系
        DataSourceUserLeaderRelation.objects.filter(data_source=data_source).delete()
        # 5. 删除数据源用户（注：密码 & 废弃密码记录会级联删除）
        DataSourceUser.objects.filter(data_source=data_source).delete()
        # 6. 删除 MPTT 树
        DepartmentRelationMPTTTree.objects.filter(data_source=data_source).delete()
        # 7. 删除数据源敏感信息
        DataSourceSensitiveInfo.objects.filter(data_source=data_source).delete()
        # 8. 删除数据源
        data_source.delete()
