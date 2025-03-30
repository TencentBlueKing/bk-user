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

import datetime
from collections import defaultdict
from typing import Dict, List, Set

from django.db import transaction
from django.utils import timezone

from bkuser.apps.data_source.models import (
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserDeprecatedPasswordRecord,
    LocalDataSourceIdentityInfo,
)
from bkuser.apps.tenant.models import TenantDepartment
from bkuser.common.constants import PERMANENT_TIME
from bkuser.common.hashers import make_password


class DataSourceUserHandler:
    @staticmethod
    def update_password(
        data_source_user: DataSourceUser,
        password: str,
        valid_days: int,
        operator: str,
    ):
        """
        更新某个用户的密码
        """
        identify_info = LocalDataSourceIdentityInfo.objects.get(user=data_source_user)
        deprecated_password = identify_info.password

        with transaction.atomic():
            identify_info.password = make_password(password)
            identify_info.password_updated_at = timezone.now()
            # 注意：更新密码会重置有效期
            if valid_days < 0:
                identify_info.password_expired_at = PERMANENT_TIME
            else:
                identify_info.password_expired_at = timezone.now() + datetime.timedelta(days=valid_days)

            identify_info.save(update_fields=["password", "password_updated_at", "password_expired_at", "updated_at"])

            DataSourceUserDeprecatedPasswordRecord.objects.create(
                user=data_source_user, password=deprecated_password, operator=operator
            )

    @staticmethod
    def batch_update_password(
        data_source_users: List[DataSourceUser],
        password: str,
        valid_days: int,
        operator: str,
    ):
        """批量更新用户的密码"""

        identify_infos = LocalDataSourceIdentityInfo.objects.filter(user__in=data_source_users)
        user_id_to_cur_password_map = {info.user_id: info.password for info in identify_infos}

        # 记录历史使用密码
        deprecated_password_records = [
            DataSourceUserDeprecatedPasswordRecord(
                user=user,
                password=user_id_to_cur_password_map.get(user.id, ""),
                operator=operator,
            )
            for user in data_source_users
        ]

        now = timezone.now()
        password_expired_at = now + datetime.timedelta(days=valid_days) if valid_days >= 0 else PERMANENT_TIME

        # Note：虽然原始密码相同，但是 make_password 中进行了加盐操作，所以每个用户的密码都必须单独 make_password，
        #  这样才能保证 DB 存储的加密串不一样。
        #  make_password 是一个耗时操作；根据测试，处理 100 个密码的平均耗时为 4.8382 秒
        for info in identify_infos:
            info.password = make_password(password)
            info.password_updated_at = now
            info.password_expired_at = password_expired_at

        with transaction.atomic():
            # 批量创建用户的历史使用密码记录
            DataSourceUserDeprecatedPasswordRecord.objects.bulk_create(deprecated_password_records, batch_size=250)

            LocalDataSourceIdentityInfo.objects.bulk_update(
                identify_infos,
                fields=["password", "password_updated_at", "updated_at"],
                batch_size=250,
            )


class DataSourceDepartmentHandler:
    @staticmethod
    def get_dept_ancestors(dept_id: int) -> List[int]:
        """
        获取某个部门的祖先部门 ID 列表
        """
        relation = DataSourceDepartmentRelation.objects.filter(department_id=dept_id).first()
        # 若该部门不存在祖先节点，则返回空列表
        if not relation:
            return []
        # 返回的祖先部门默认以降序排列，从根祖先部门 -> 父部门
        return list(relation.get_ancestors().values_list("department_id", flat=True))


class TenantDepartmentHandler:
    @staticmethod
    def get_tenant_department_parent_id_map(
        tenant_id: str, tenant_departments: List[TenantDepartment]
    ) -> Dict[int, int]:
        """
        获取部门的父部门 ID 映射
        """

        # 获取部门的数据源部门 ID 列表
        dept_ids = [dept.data_source_department_id for dept in tenant_departments]

        # 获取部门的数据源部门关系
        parent_id_map = dict(
            DataSourceDepartmentRelation.objects.filter(department_id__in=dept_ids).values_list(
                "department_id", "parent_id"
            )
        )
        # 获取父部门数据源 ID 到租户父部门 ID 的映射
        parent_ids = list(parent_id_map.values())
        tenant_dept_id_map = dict(
            TenantDepartment.objects.filter(tenant_id=tenant_id, data_source_department_id__in=parent_ids).values_list(
                "data_source_department_id", "id"
            )
        )

        return {
            dept.id: tenant_dept_id_map[parent_id_map[dept.data_source_department_id]]
            for dept in tenant_departments
            if parent_id_map[dept.data_source_department_id] in tenant_dept_id_map
        }

    @staticmethod
    def get_has_child_map(data_source_department_ids: List[int]) -> dict[int, bool]:
        """获取部门是否有子部门的信息"""
        # TODO: 这里存在性能问题，后续添加缓存优化
        dept_has_child_ids = set(
            DataSourceDepartmentRelation.objects.filter(parent_id__in=data_source_department_ids)
            .values_list("parent_id", flat=True)
            .distinct()
        )

        return {dept_id: dept_id in dept_has_child_ids for dept_id in data_source_department_ids}

    @staticmethod
    def get_has_user_map(data_source_department_ids: List[int]) -> dict[int, bool]:
        """获取部门是否有所属用户的信息"""
        # TODO: 这里存在性能问题，后续添加缓存优化
        dept_has_user_ids = set(
            DataSourceDepartmentUserRelation.objects.filter(department_id__in=data_source_department_ids)
            .values_list("department_id", flat=True)
            .distinct()
        )

        return {dept_id: dept_id in dept_has_user_ids for dept_id in data_source_department_ids}


class TenantOrgPathHandler:
    @staticmethod
    def get_dept_organization_path_map(data_source_department_ids: List[int]) -> Dict[int, str]:
        """获取租户部门的组织路径信息"""

        # 数据源部门 ID -> 组织路径
        org_path_map = TenantOrgPathHandler._query_org_path(data_source_department_ids, include_self=False)

        # 部门 ID -> 组织路径
        return {dept_id: org_path_map.get(dept_id, "") for dept_id in data_source_department_ids}

    @staticmethod
    def get_user_organization_paths_map(data_source_user_ids: List[int]) -> dict[int, List[str]]:
        """获取租户用户的组织路径信息"""

        # 数据源用户 ID -> [数据源部门 ID1， 数据源部门 ID2]
        user_dept_id_map = defaultdict(list)
        for relation in DataSourceDepartmentUserRelation.objects.filter(user_id__in=data_source_user_ids):
            user_dept_id_map[relation.user_id].append(relation.department_id)

        # 数据源部门 ID 集合
        data_source_dept_ids: Set[int] = set().union(*user_dept_id_map.values())

        # 数据源部门 ID -> 组织路径
        org_path_map = TenantOrgPathHandler._query_org_path(list(data_source_dept_ids), include_self=True)

        # 用户 ID -> 组织路径列表
        return {
            user_id: [org_path_map[dept_id] for dept_id in user_dept_id_map[user_id] if dept_id in org_path_map]
            for user_id in data_source_user_ids
        }

    @staticmethod
    def _query_org_path(data_source_department_ids: List[int], include_self: bool) -> Dict[int, str]:
        """构建部门 ID -> 组织路径映射"""
        relations = DataSourceDepartmentRelation.objects.select_related("department").filter(
            department_id__in=data_source_department_ids
        )
        org_path_map = {}
        # TODO: 这里存在 N + 1 问题，后续添加缓存优化或其他方式优化祖先路径的批量快速获取
        for rel in relations:
            dept_names = list(rel.get_ancestors(include_self=include_self).values_list("department__name", flat=True))
            org_path_map[rel.department_id] = "/".join(dept_names)
        return org_path_map
