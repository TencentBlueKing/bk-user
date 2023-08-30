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
from typing import Dict, List

from django.db import transaction
from pydantic import BaseModel

from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.tenant.models import Tenant, TenantUser
from bkuser.utils.uuid import generate_uuid


class DataSourceUserBaseInfo(BaseModel):
    """数据源用户基础信息"""

    username: str
    full_name: str
    email: str
    phone: str
    phone_country_code: str


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
            user = DataSourceUser.objects.create(data_source=data_source, **base_user_info.model_dump())

            # 批量创建数据源用户-部门关系
            department_user_relation_objs = [
                DataSourceDepartmentUserRelation(department_id=dept_id, user_id=user.id)
                for dept_id in relation_info.department_ids
            ]

            if department_user_relation_objs:
                DataSourceDepartmentUserRelation.objects.bulk_create(department_user_relation_objs)

            # 批量创建数据源用户-上级关系
            user_leader_relation_objs = [
                DataSourceUserLeaderRelation(leader_id=leader_id, user_id=user.id)
                for leader_id in relation_info.leader_ids
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

    @staticmethod
    def update_user_department_relations(user: DataSourceUser, department_ids: List):
        """
        更新用户-部门关系
        """
        # 查询是否存在现有关系，有则跳过，无则增加
        department_user_relation_objs: List = []
        should_deleted_department_user_relation_ids: List = []

        old_department_user_relations = DataSourceDepartmentUserRelation.objects.filter(user=user)
        # Note: 有新关系可能存在重复数据，所以这里使用不变的old_department_set用于后续判断是否存在的依据，
        # 而不使用后面会变更的old_department_relations数据
        old_department_set = {r.department for r in old_department_user_relations}
        old_department_relations = {r.department: r.id for r in old_department_user_relations}

        departments = DataSourceDepartment.objects.filter(id__in=department_ids)
        for department in departments:
            # 用户-部门关系已存在
            if department in old_department_set:
                # Note: 可能本次更新里存在重复数据，dict无法重复移除
                if department in old_department_relations:
                    del old_department_relations[department]
                continue

            # 不存在则添加
            department_user_relation_objs.append(DataSourceDepartmentUserRelation(department=department, user=user))

        if department_user_relation_objs:
            DataSourceDepartmentUserRelation.objects.bulk_create(department_user_relation_objs)

        # 已存在的数据从old_department_relations移除后，最后剩下的数据，表示多余的：
        # 即本次更新里不存在的用户部门关系，需要删除
        if len(old_department_relations) > 0:
            should_deleted_department_user_relation_ids.extend(old_department_relations.values())
            DataSourceDepartmentUserRelation.objects.filter(
                id__in=should_deleted_department_user_relation_ids
            ).delete()

    @staticmethod
    def update_user_leader_relations(user: DataSourceUser, leader_ids: List):
        """更新用户-上级关系"""
        user_leader_relation_objs: List = []
        should_deleted_user_leader_relation_ids: List = []

        old_user_leader_relations = DataSourceUserLeaderRelation.objects.filter(user=user)
        # Note: 有新关系可能存在重复数据，所以这里使用不变的old_leader_set用于后续判断是否存在的依据，
        # 而不使用后面会变更的old_leader_relations数据
        old_leader_set = {r.leader for r in old_user_leader_relations}
        old_leader_relations = {r.leader: r.id for r in old_user_leader_relations}

        leaders = DataSourceUser.objects.filter(id__in=leader_ids)
        for leader in leaders:
            # 用户-上级关系已存在
            if leader in old_leader_set:
                # Note: 可能本次更新里存在重复数据，dict无法重复移除
                if leader in old_leader_relations:
                    del old_leader_relations[leader]
                continue

            # 不存在则添加
            user_leader_relation_objs.append(DataSourceUserLeaderRelation(leader=leader, user=user))

        if user_leader_relation_objs:
            DataSourceUserLeaderRelation.objects.bulk_create(user_leader_relation_objs)

        # 已存在的数据从old_leader_relations移除后，最后剩下的数据，表示多余的：
        # 即本次更新里不存在的用户上级关系，需要删除
        if len(old_leader_relations) > 0:
            should_deleted_user_leader_relation_ids.extend(old_leader_relations.values())
            DataSourceUserLeaderRelation.objects.filter(id__in=should_deleted_user_leader_relation_ids).delete()

    @staticmethod
    def update_user(
        user: DataSourceUser, base_user_info: DataSourceUserEditableBaseInfo, relation_info: DataSourceUserRelationInfo
    ):
        """更新数据源用户"""

        with transaction.atomic():
            # 更新用户基础信息
            for key, value in base_user_info:
                setattr(user, key, value)
            user.save()

            # 更新用户-部门关系
            DataSourceOrganizationHandler.update_user_department_relations(
                user=user, department_ids=relation_info.department_ids
            )

            # 更新用户-上级关系
            DataSourceOrganizationHandler.update_user_leader_relations(user=user, leader_ids=relation_info.leader_ids)

    @staticmethod
    def get_department_info_map_by_id(department_ids: List[int]) -> List[DataSourceUserDepartmentInfo]:
        """
        根据部门ID获取部门信息
        """
        departments = DataSourceDepartment.objects.filter(id__in=department_ids)
        data: List[DataSourceUserDepartmentInfo] = [
            DataSourceUserDepartmentInfo(
                id=dept.id,
                name=dept.name,
            )
            for dept in departments
        ]

        return data

    @staticmethod
    def get_user_department_ids_map(user_ids: List[int]) -> Dict[int, List[int]]:
        """
        获取 用户-所属部门ID关系 映射
        """
        department_user_relations = DataSourceDepartmentUserRelation.objects.filter(user_id__in=user_ids)
        user_department_ids_map = defaultdict(list)
        for r in department_user_relations:
            user_id = r.user_id
            department_id = r.department_id
            if r.user_id in user_department_ids_map:
                user_department_ids_map[user_id].append(department_id)
            else:
                user_department_ids_map[user_id] = [department_id]

        return user_department_ids_map

    @staticmethod
    def get_user_departments_map_by_user_id(user_ids: List[int]) -> Dict[int, List[DataSourceUserDepartmentInfo]]:
        """
        获取 用户-所有归属部门信息
        """
        user_department_ids_map = DataSourceOrganizationHandler.get_user_department_ids_map(user_ids=user_ids)

        data: Dict = {}
        for user_id in user_ids:
            department_ids = user_department_ids_map.get(user_id) or []
            if not department_ids:
                continue
            department_infos = DataSourceOrganizationHandler.get_department_info_map_by_id(
                department_ids=department_ids
            )

            data[user_id] = department_infos

        return data

    @staticmethod
    def get_user_leader_ids_map(user_ids: List[int]) -> Dict[int, List[int]]:
        """
        获取用户-所有上级ID关系映射
        """
        user_leader_relations = DataSourceUserLeaderRelation.objects.prefetch_related("leader").filter(
            user_id__in=user_ids
        )

        user_leader_ids_map = defaultdict(list)
        for r in user_leader_relations:
            leader_id = r.leader_id
            if r.user_id in user_leader_ids_map:
                user_leader_ids_map[r.user_id].append(leader_id)
            else:
                user_leader_ids_map[r.user_id] = [leader_id]
        return user_leader_ids_map

    @staticmethod
    def get_leader_info_map_by_id(leaders_ids: List[int]) -> List[DataSourceUserLeaderInfo]:
        """
        根据上级ID获取上级信息
        """
        leaders = DataSourceUser.objects.filter(id__in=leaders_ids)
        data: List[DataSourceUserLeaderInfo] = [
            DataSourceUserLeaderInfo(
                id=leader.id,
                username=leader.username,
            )
            for leader in leaders
        ]

        return data

    @staticmethod
    def get_user_leaders_map_by_user_id(user_ids: List[int]):
        """
        获取用户-所有上级信息数据
        """
        user_leader_ids_map = DataSourceOrganizationHandler.get_user_leader_ids_map(user_ids=user_ids)
        data: Dict = {}
        for user_id in user_ids:
            leaders_ids = user_leader_ids_map.get(user_id) or []
            if not leaders_ids:
                continue
            leader_infos = DataSourceOrganizationHandler.get_leader_info_map_by_id(leaders_ids=leaders_ids)

            data[user_id] = leader_infos
        return data
