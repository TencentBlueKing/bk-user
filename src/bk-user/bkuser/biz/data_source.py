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

from bkuser.apps.data_source.models import DataSource, DataSourceDepartment, DataSourceDepartmentRelation
from bkuser.common.error_codes import error_codes


class DataSourceDepartmentInfo(BaseModel):
    id: int
    name: str
    data_source_id: int
    children: list
    full_name: str


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


class DataSourceDepartmentHandler:
    @staticmethod
    def retrieve_department(department_id: int) -> DataSourceDepartmentInfo:
        """
        获取单个部门信息
        """
        try:
            # 生成组织架构路径
            parent_ids = (
                DataSourceDepartmentRelation.objects.get(id=department_id)
                .get_ancestors(include_self=True)
                .values_list("id", flat=True)
            )
            parents = DataSourceDepartment.objects.filter(id__in=parent_ids).values_list("name", flat=True)
            full_name = "/".join(list(parents))
            # 构建基础信息
            department = DataSourceDepartment.objects.get(id=department_id)
            base_info = {
                "id": department.id,
                "name": department.name,
                "full_name": full_name,
                "data_source_id": department.data_source_id,
                "children": DataSourceDepartmentRelation.objects.filter(parent_id=department.id).values(
                    "id", flat=True
                ),
            }
            return DataSourceDepartmentInfo(**base_info)
        except DataSourceDepartment.DoesNotExist:
            raise error_codes.OBJECT_NOT_FOUND
