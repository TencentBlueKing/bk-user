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
from typing import Dict, List

from django.db import transaction
from django.utils import timezone
from pydantic import BaseModel

from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.tenant.models import Tenant, TenantUser, TenantUserValidityPeriodConfig
from bkuser.utils.uuid import generate_uuid


class DataSourceUserBaseInfo(BaseModel):
    """数据源用户基础信息"""

    username: str
    full_name: str
    email: str
    phone: str
    phone_country_code: str
    logo: str


class DataSourceUserEditableBaseInfo(BaseModel):
    """数据源用户可编辑的基础信息"""

    full_name: str
    email: str
    phone: str
    phone_country_code: str
    logo: str


class DataSourceUserDepartmentInfo(BaseModel):
    """数据源用户部门信息"""

    id: int
    name: str


class DataSourceUserLeaderInfo(BaseModel):
    """数据源用户上级信息"""

    id: int
    username: str


class DataSourceUserRelationInfo(BaseModel):
    """数据源用户关系信息"""

    department_ids: List[int]
    leader_ids: List[int]


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
            user = DataSourceUser.objects.create(
                data_source=data_source, code=base_user_info.username, **base_user_info.model_dump()
            )

            # 批量创建数据源用户-部门关系
            department_user_relation_objs = [
                DataSourceDepartmentUserRelation(department_id=dept_id, user_id=user.id, data_source=data_source)
                for dept_id in relation_info.department_ids
            ]

            if department_user_relation_objs:
                DataSourceDepartmentUserRelation.objects.bulk_create(department_user_relation_objs)

            # 批量创建数据源用户-上级关系
            user_leader_relation_objs = [
                DataSourceUserLeaderRelation(leader_id=leader_id, user_id=user.id, data_source=data_source)
                for leader_id in relation_info.leader_ids
            ]

            if user_leader_relation_objs:
                DataSourceUserLeaderRelation.objects.bulk_create(user_leader_relation_objs)

            # 查询关联的租户
            tenant = Tenant.objects.get(id=data_source.owner_tenant_id)

            # 创建租户用户
            tenant_user = TenantUser(
                data_source_user=user,
                tenant=tenant,
                data_source=data_source,
                id=generate_uuid(),
            )

            # 根据配置初始化账号有效期
            cfg = TenantUserValidityPeriodConfig.objects.get(tenant_id=tenant.id)
            if cfg.enabled and cfg.validity_period > 0:
                tenant_user.account_expired_at = timezone.now() + datetime.timedelta(days=cfg.validity_period)
            # 入库
            tenant_user.save()
        return user.id

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
        user: DataSourceUser, base_user_info: DataSourceUserEditableBaseInfo, relation_info: DataSourceUserRelationInfo
    ):
        """更新数据源用户"""

        with transaction.atomic():
            # 更新用户基础信息
            user.full_name = base_user_info.full_name
            user.email = base_user_info.email
            user.phone = base_user_info.phone
            user.phone_country_code = base_user_info.phone_country_code
            user.logo = base_user_info.logo

            user.save()

            # 更新用户-部门关系
            DataSourceOrganizationHandler.update_user_department_relations(
                user=user, department_ids=relation_info.department_ids
            )

            # 更新用户-上级关系
            DataSourceOrganizationHandler.update_user_leader_relations(user=user, leader_ids=relation_info.leader_ids)

    @staticmethod
    def list_department_info_by_id(department_ids: List[int]) -> List[DataSourceUserDepartmentInfo]:
        """
        根据部门ID获取部门信息
        """
        return [
            DataSourceUserDepartmentInfo(id=dept.id, name=dept.name)
            for dept in DataSourceDepartment.objects.filter(id__in=department_ids)
        ]

    @staticmethod
    def get_user_department_ids_map(user_ids: List[int]) -> Dict[int, List[int]]:
        """
        获取 用户-所属部门ID关系 映射
        """
        department_user_relations = DataSourceDepartmentUserRelation.objects.filter(user_id__in=user_ids)
        user_department_ids_map = defaultdict(list)
        for r in department_user_relations:
            user_department_ids_map[r.user_id].append(r.department_id)

        return user_department_ids_map

    @staticmethod
    def get_user_departments_map_by_user_id(user_ids: List[int]) -> Dict[int, List[DataSourceUserDepartmentInfo]]:
        """
        获取 用户-所有归属部门信息
        """
        user_department_ids_map = DataSourceOrganizationHandler.get_user_department_ids_map(user_ids=user_ids)

        data: Dict = {}
        for user_id in user_ids:
            department_ids = user_department_ids_map.get(user_id)
            if not department_ids:
                continue
            data[user_id] = DataSourceOrganizationHandler.list_department_info_by_id(department_ids=department_ids)

        return data

    @staticmethod
    def get_user_leader_ids_map(user_ids: List[int]) -> Dict[int, List[int]]:
        """
        获取用户-所有上级ID关系映射
        """
        user_leader_relations = DataSourceUserLeaderRelation.objects.filter(user_id__in=user_ids)

        user_leader_ids_map = defaultdict(list)
        for r in user_leader_relations:
            user_leader_ids_map[r.user_id].append(r.leader_id)

        return user_leader_ids_map

    @staticmethod
    def list_leader_info_by_id(leaders_ids: List[int]) -> List[DataSourceUserLeaderInfo]:
        """
        根据上级ID获取上级信息
        """
        return [
            DataSourceUserLeaderInfo(id=leader.id, username=leader.username)
            for leader in DataSourceUser.objects.filter(id__in=leaders_ids)
        ]

    @staticmethod
    def get_user_leaders_map_by_user_id(user_ids: List[int]):
        """
        获取用户-所有上级信息数据
        """
        user_leader_ids_map = DataSourceOrganizationHandler.get_user_leader_ids_map(user_ids=user_ids)

        data: Dict = {}
        for user_id in user_ids:
            leaders_ids = user_leader_ids_map.get(user_id)
            if not leaders_ids:
                continue
            data[user_id] = DataSourceOrganizationHandler.list_leader_info_by_id(leaders_ids=leaders_ids)

        return data
