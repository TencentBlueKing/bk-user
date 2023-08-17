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

from django.db import transaction
from pydantic import BaseModel

from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.tenant.models import Tenant, TenantUser
from bkuser.utils.uuid import generate_uuid


class DataSourceUserBaseInfo(
    BaseModel,
):
    """数据源用户基础信息"""

    username: str
    full_name: str
    email: str
    phone: str
    phone_country_code: str


class DataSourceUserRelationInfo(
    BaseModel,
):
    """数据源用户关系信息"""

    department_ids: List
    leader_ids: List


class DataSourceOrganizationHandler:
    @staticmethod
    def create_user(
        data_source: DataSource, base_user_info: DataSourceUserBaseInfo, relation_info: DataSourceUserRelationInfo
    ) -> str:
        """
        创建数据源用户
        """
        # TODO：补充日志
        with transaction.atomic():
            # 创建数据源用户
            create_user_info_map = {"data_source": data_source, **base_user_info.model_dump()}
            user = DataSourceUser.objects.create(**create_user_info_map)

            # 批量创建数据源用户-部门关系
            department_user_relation_objs = [
                DataSourceDepartmentUserRelation(department_id=department_id, user_id=user.id)
                for department_id in relation_info.model_dump()["department_ids"]
            ]

            if department_user_relation_objs:
                DataSourceDepartmentUserRelation.objects.bulk_create(department_user_relation_objs, batch_size=100)

            # 批量创建数据源用户-上级关系
            user_leader_relation_objs = [
                DataSourceUserLeaderRelation(leader_id=leader_id, user_id=user.id)
                for leader_id in relation_info.model_dump()["leader_ids"]
            ]

            if user_leader_relation_objs:
                DataSourceUserLeaderRelation.objects.bulk_create(user_leader_relation_objs)

            # 查询关联的租户
            tenant = Tenant.objects.get(id=data_source.owner_tenant_id)
            # 创建租户用户
            TenantUser.objects.create(
                data_source_user=user,
                tenant=tenant,
                data_source=data_source,
                id=generate_uuid(),
            )

        return user.id
