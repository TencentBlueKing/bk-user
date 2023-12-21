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
from collections import defaultdict
from typing import Any, Dict, List

from django.db import transaction
from django.utils import timezone
from pydantic import BaseModel

from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.data_source.utils import gen_tenant_user_id
from bkuser.apps.tenant.models import TenantUser, TenantUserValidityPeriodConfig


class DataSourceUserInfo(BaseModel):
    """数据源用户基础信息"""

    username: str
    full_name: str
    email: str
    phone: str
    phone_country_code: str
    logo: str
    extras: Dict[str, Any]


class DataSourceUserEditableInfo(BaseModel):
    """数据源用户可编辑的基础信息"""

    full_name: str
    email: str
    phone: str
    phone_country_code: str
    logo: str
    extras: Dict[str, Any]


class DataSourceUserRelationInfo(BaseModel):
    """数据源用户关系信息"""

    department_ids: List[int]
    leader_ids: List[int]


class DataSourceUserHandler:
    @staticmethod
    def create_user(data_source: DataSource, user_info: DataSourceUserInfo, relation_info: DataSourceUserRelationInfo):
        """创建数据源用户"""

        with transaction.atomic():
            # 创建数据源用户
            user = DataSourceUser.objects.create(
                data_source=data_source, code=user_info.username, **user_info.model_dump()
            )

            # 批量创建数据源用户-部门关系
            department_user_relations = [
                DataSourceDepartmentUserRelation(department_id=dept_id, user_id=user.id, data_source=data_source)
                for dept_id in relation_info.department_ids
            ]

            if department_user_relations:
                DataSourceDepartmentUserRelation.objects.bulk_create(department_user_relations)

            # 批量创建数据源用户-上级关系
            user_leader_relations = [
                DataSourceUserLeaderRelation(leader_id=leader_id, user_id=user.id, data_source=data_source)
                for leader_id in relation_info.leader_ids
            ]

            if user_leader_relations:
                DataSourceUserLeaderRelation.objects.bulk_create(user_leader_relations)

            # 默认会同步到当前数据源所属的租户 TODO (su) 考虑租户协同场景
            tenant_id = data_source.owner_tenant_id
            # 创建租户用户
            tenant_user = TenantUser(
                id=gen_tenant_user_id(tenant_id, data_source, user),
                data_source_user=user,
                tenant_id=tenant_id,
                data_source=data_source,
            )

            # 根据配置初始化账号有效期
            cfg = TenantUserValidityPeriodConfig.objects.get(tenant_id=tenant_id)
            if cfg.enabled and cfg.validity_period > 0:
                tenant_user.account_expired_at = timezone.now() + datetime.timedelta(days=cfg.validity_period)

            tenant_user.save()

    @staticmethod
    def update_user_department_relations(user: DataSourceUser, department_ids: List):
        """
        更新用户-部门关系
        """
        # 查询旧用户部门信息
        old_department_ids = DataSourceDepartmentUserRelation.objects.filter(user=user).values_list(
            "department_id", flat=True
        )

        # 需要新增的用户部门信息
        should_created_department_ids = set(department_ids) - set(old_department_ids)
        # 需要删除的用户部门信息
        should_deleted_department_ids = set(old_department_ids) - set(department_ids)

        # DB新增
        if should_created_department_ids:
            should_created_relations = [
                DataSourceDepartmentUserRelation(department_id=department_id, user=user, data_source=user.data_source)
                for department_id in should_created_department_ids
            ]
            DataSourceDepartmentUserRelation.objects.bulk_create(should_created_relations)

        # DB删除
        if should_deleted_department_ids:
            DataSourceDepartmentUserRelation.objects.filter(
                user=user, department_id__in=should_deleted_department_ids
            ).delete()

    @staticmethod
    def update_user_leader_relations(user: DataSourceUser, leader_ids: List):
        """更新用户-上级关系"""
        # 查询旧用户上级信息
        old_leader_ids = DataSourceUserLeaderRelation.objects.filter(user=user).values_list("leader_id", flat=True)

        # 需要新增的用户部门信息
        should_created_leader_ids = set(leader_ids) - set(old_leader_ids)
        # 需要删除的用户部门信息
        should_deleted_leader_ids = set(old_leader_ids) - set(leader_ids)

        # DB新增
        if should_created_leader_ids:
            should_created_relations = [
                DataSourceUserLeaderRelation(leader_id=leader_id, user=user, data_source=user.data_source)
                for leader_id in should_created_leader_ids
            ]
            DataSourceUserLeaderRelation.objects.bulk_create(should_created_relations)

        # DB删除
        if should_deleted_leader_ids:
            DataSourceUserLeaderRelation.objects.filter(user=user, leader_id__in=should_deleted_leader_ids).delete()

    @staticmethod
    def update_user(
        user: DataSourceUser, user_info: DataSourceUserEditableInfo, relation_info: DataSourceUserRelationInfo
    ):
        """更新数据源用户"""

        with transaction.atomic():
            # 更新用户基础信息
            user.full_name = user_info.full_name
            user.email = user_info.email
            user.phone = user_info.phone
            user.phone_country_code = user_info.phone_country_code
            user.logo = user_info.logo
            user.extras.update(user_info.extras)
            user.save()

            # 更新用户-部门关系
            DataSourceUserHandler.update_user_department_relations(
                user=user, department_ids=relation_info.department_ids
            )

            # 更新用户-上级关系
            DataSourceUserHandler.update_user_leader_relations(user=user, leader_ids=relation_info.leader_ids)


class DataSourceDepartmentHandler:
    @staticmethod
    def get_sub_data_source_dept_ids_map(parent_dept_ids: List[int]) -> Dict[int, List[int]]:
        """获取一批数据源部门的子部门 id 列表信息（不包含递归部门）"""
        sub_dept_ids_map = defaultdict(list)
        # 注：当前 MPTT 模型中，parent_id 等价于 parent__department_id
        for rel in DataSourceDepartmentRelation.objects.filter(parent_id__in=parent_dept_ids):
            sub_dept_ids_map[rel.parent_id].append(rel.department_id)

        return sub_dept_ids_map
