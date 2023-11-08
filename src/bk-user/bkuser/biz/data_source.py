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
from collections import defaultdict
from typing import Dict, List, Optional

from pydantic import BaseModel

from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourcePlugin,
    DataSourceUserLeaderRelation,
)
from bkuser.biz.data_source_plugin import DefaultPluginConfigProvider
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig, PasswordInitialConfig


class DataSourceDepartmentInfoWithChildren(BaseModel):
    id: int
    name: str
    children_ids: List[int]


class DataSourceSimpleInfo(BaseModel):
    id: int
    name: str


class DataSourceHandler:
    @staticmethod
    def get_data_source_map_by_owner(
        owner_tenant_ids: Optional[List[str]] = None,
    ) -> Dict[str, List[DataSourceSimpleInfo]]:
        """
        查询数据源
        """
        data_sources = DataSource.objects.all()
        if owner_tenant_ids is not None:
            data_sources = data_sources.filter(owner_tenant_id__in=owner_tenant_ids)

        data = defaultdict(list)
        for i in data_sources:
            data[i.owner_tenant_id].append(DataSourceSimpleInfo(id=i.id, name=i.name))

        return data

    @staticmethod
    def create_local_data_source_with_merge_config(
        data_source_name: str,
        owner_tenant_id: str,
        password_initial_config: PasswordInitialConfig,
    ) -> DataSource:
        """使用与默认配置合并后的插件配置，创建本地数据源"""
        plugin_id = DataSourcePluginEnum.LOCAL
        plugin_config: LocalDataSourcePluginConfig = DefaultPluginConfigProvider().get(plugin_id)  # type: ignore
        plugin_config.password_initial = password_initial_config

        return DataSource.objects.create(
            name=data_source_name,
            owner_tenant_id=owner_tenant_id,
            plugin=DataSourcePlugin.objects.get(id=plugin_id),
            plugin_config=plugin_config,
        )


class DataSourceDepartmentHandler:
    @staticmethod
    def get_department_info_map_by_ids(department_ids: List[int]) -> Dict[int, DataSourceDepartmentInfoWithChildren]:
        """
        获取部门基础信息
        """
        departments_map: Dict = {}
        for dept in DataSourceDepartment.objects.filter(id__in=department_ids):
            departments_map[dept.id] = DataSourceDepartmentInfoWithChildren(
                id=dept.id,
                name=dept.name,
                children_ids=list(
                    DataSourceDepartmentRelation.objects.get(department=dept)
                    .get_children()
                    .values_list("department_id", flat=True)
                ),
            )

        return departments_map

    @staticmethod
    def list_department_user_ids(department_id: int, recursive: bool = True) -> List[str]:
        """
        获取部门下用户id列表
        """
        # 是否返回子部门用户
        if not recursive:
            return list(
                DataSourceDepartmentUserRelation.objects.filter(
                    department_id=department_id,
                ).values_list("user_id", flat=True)
            )

        department = DataSourceDepartmentRelation.objects.get(department_id=department_id)
        recursive_department_ids = department.get_descendants(include_self=True).values_list(
            "department_id", flat=True
        )
        return list(
            DataSourceDepartmentUserRelation.objects.filter(
                department_id__in=recursive_department_ids,
            ).values_list("user_id", flat=True)
        )

    @staticmethod
    def get_user_department_ids_map(user_ids: List[int]) -> Dict[int, List[int]]:
        """
        批量获取数据源用户部门 id 信息

        :param user_ids: 数据源用户 ID 列表
        :returns: 多个数据源用户部门 ID 列表
        """
        user_department_ids_map = defaultdict(list)
        for item in DataSourceDepartmentUserRelation.objects.filter(user_id__in=user_ids):
            user_department_ids_map[item.user_id].append(item.department_id)

        return user_department_ids_map


class DataSourceUserHandler:
    @staticmethod
    def get_user_leader_ids_map(user_ids: List[int]) -> Dict[int, List[int]]:
        """
        批量获取数据源用户 leader id 信息

        :param user_ids: 数据源用户 ID 列表
        :returns: 多个数据源用户 leader ID 列表
        """
        leaders_map = defaultdict(list)
        for relation in DataSourceUserLeaderRelation.objects.filter(user_id__in=user_ids):
            leaders_map[relation.user_id].append(relation.leader_id)

        return leaders_map
