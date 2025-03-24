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

from collections import defaultdict
from functools import cached_property
from typing import Dict, List, Set

from apigw_manager.drf.authentication import ApiGatewayJWTAuthentication
from django.db.models import Prefetch, Q, QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
)
from bkuser.apps.tenant.models import TenantDepartment, TenantUser


class OpenWebApiCommonMixin:
    authentication_classes = [ApiGatewayJWTAuthentication]
    permission_classes = [IsAuthenticated]

    request: Request

    TenantHeaderKey = "HTTP_X_BK_TENANT_ID"

    @cached_property
    def tenant_id(self) -> str:
        tenant_id = self.request.META.get(self.TenantHeaderKey)

        if not tenant_id:
            raise ValidationError("X-Bk-Tenant-Id header is required")

        return tenant_id

    @cached_property
    def real_data_source_id(self) -> int:
        data_source = (
            DataSource.objects.filter(owner_tenant_id=self.tenant_id, type=DataSourceTypeEnum.REAL).only("id").first()
        )
        if not data_source:
            raise ValidationError(_("当前租户不存在实名用户数据源"))

        return data_source.id


class TenantDeptOrgPathMapMixin:
    def _get_dept_organization_path_map(self, tenant_depts: QuerySet[TenantDepartment]) -> Dict[int, str]:
        """获取租户部门的组织路径信息"""
        data_source_dept_ids = {dept.data_source_department_id for dept in tenant_depts}

        # 获取部门关系及所有需要的祖先节点
        relations = self._get_relations_with_ancestors(data_source_dept_ids)
        # 数据源部门 ID -> 组织路径
        org_path_map = self._build_org_path_map(relations, include_self=False)

        # 租户部门 ID -> 组织路径
        return {
            dept.id: org_path_map.get(dept.data_source_department_id, dept.data_source_department.name)
            for dept in tenant_depts
        }

    def _get_user_organization_paths_map(self, tenant_users: QuerySet[TenantUser]) -> Dict[str, List[str]]:
        """获取租户用户的组织路径信息"""
        data_source_user_ids = [tenant_user.data_source_user_id for tenant_user in tenant_users]

        # 数据源用户 ID -> [数据源部门 ID1， 数据源部门 ID2]
        user_dept_id_map = defaultdict(list)
        for relation in DataSourceDepartmentUserRelation.objects.filter(user_id__in=data_source_user_ids):
            user_dept_id_map[relation.user_id].append(relation.department_id)

        # 数据源部门 ID 集合
        data_source_dept_ids: Set[int] = set().union(*user_dept_id_map.values())

        # 获取部门关系及所有需要的祖先节点
        relations = self._get_relations_with_ancestors(data_source_dept_ids)
        # 数据源部门 ID -> 组织路径
        org_path_map = self._build_org_path_map(relations)

        # 租户用户 ID -> 组织路径列表
        return {
            user.id: [
                org_path_map[dept_id]
                for dept_id in user_dept_id_map[user.data_source_user_id]
                if dept_id in org_path_map
            ]
            for user in tenant_users
        }

    @staticmethod
    def _get_relations_with_ancestors(data_source_dept_ids: Set[int]) -> QuerySet[DataSourceDepartmentRelation]:
        """获取部门关系及预取所有需要的祖先节点"""
        # 按照左值排序，确保祖先节点在后续查询中已经加载
        relations = (
            DataSourceDepartmentRelation.objects.select_related("department")
            .filter(department_id__in=data_source_dept_ids)
            .order_by("tree_id", "lft")
        )

        # 按tree_id分组处理不同树结构
        tree_groups = defaultdict(list)
        for rel in relations:
            tree_groups[rel.tree_id].append(rel)

        # 构造组合查询条件：对每个tree_id生成范围条件
        combined_query = Q()
        for tree_id, group in tree_groups.items():
            # 计算当前 tree 中需要覆盖的左右值范围
            max_lft = max(rel.lft for rel in group)
            min_rght = min(rel.rght for rel in group)
            # 组合查询条件：覆盖这些节点的所有祖先（左值小于等于当前最大左值，右值大于等于当前最小右值）
            combined_query |= Q(lft__lte=max_lft, rght__gte=min_rght, tree_id=tree_id)

        # 批量预取父部门（单次查询完成所有祖先部门的获取）
        return relations.prefetch_related(
            Prefetch(
                "parent",
                queryset=DataSourceDepartmentRelation.objects.select_related("department").filter(combined_query),
            )
        )

    @staticmethod
    def _build_org_path_map(
        relations: QuerySet[DataSourceDepartmentRelation], include_self: bool = True
    ) -> Dict[int, str]:
        """构建部门 ID -> 组织路径映射"""
        # 数据源部门 ID -> 路径片段
        path_cache: Dict[int, List] = {}
        # 数据源部门 ID -> 组织路径
        org_path_map: Dict[int, str] = {}

        for rel in relations:
            # 如果父部门已经计算过路径，直接拼接
            if rel.parent and rel.parent.department_id in path_cache:
                current_path = path_cache[rel.parent.department_id] + [rel.department.name]
            else:
                current_path = [rel.department.name]
                current_parent = rel.parent
                # 递归获取所有祖先节点
                while current_parent:
                    current_path.append(current_parent.department.name)
                    current_parent = current_parent.parent

                # 反转路径，使得路径从根节点到当前节点
                current_path = list(reversed(current_path))

            path_cache[rel.department_id] = current_path

            # 若 include_self 为 False，则不包含当前节点
            org_path_map[rel.department_id] = "/".join(
                current_path[: None if include_self else -1] if current_path else []
            )

        return org_path_map
