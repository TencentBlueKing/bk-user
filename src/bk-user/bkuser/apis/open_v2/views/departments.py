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

import operator
from functools import reduce
from typing import Any, Dict, List

from django.db.models import Q, QuerySet
from django.http import Http404
from rest_framework import generics
from rest_framework.response import Response

from bkuser.apis.open_v2.mixins import DefaultTenantMixin, LegacyOpenApiCommonMixin
from bkuser.apis.open_v2.pagination import LegacyOpenApiPagination
from bkuser.apis.open_v2.serializers.departments import (
    DepartmentListInputSLZ,
    DepartmentRetrieveInputSLZ,
    ProfileDepartmentListInputSLZ,
)
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
)
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.common.error_codes import error_codes
from bkuser.utils.tree import Tree


class DepartmentListApi(LegacyOpenApiCommonMixin, DefaultTenantMixin, generics.ListAPIView):
    """查询部门列表"""

    pagination_class = LegacyOpenApiPagination

    def get(self, request, *args, **kwargs):
        slz = DepartmentListInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data
        no_page = params["no_page"]

        tenant_depts = self._filter_queryset(params)
        if not no_page:
            tenant_depts = self.paginate_queryset(tenant_depts)

        dept_infos = self._build_dept_infos(tenant_depts, params.get("fields", []), params["with_ancestors"])
        if not no_page:
            return self.get_paginated_response(dept_infos)

        return Response(dept_infos)

    def _build_dept_infos(
        self, tenant_depts: QuerySet[TenantDepartment], fields: List[str], with_ancestors: bool
    ) -> List[Dict[str, Any]]:
        # 部门 ID 映射：{(数据源部门 ID, 租户 ID)：租户部门 ID}
        tenant_dept_id_map = {
            (data_source_dept_id, tenant_id): dept_id
            for (data_source_dept_id, tenant_id, dept_id) in TenantDepartment.objects.values_list(
                "data_source_department_id", "tenant_id", "id"
            )
        }
        # {数据源部门 ID: 数据源部门名称}
        dept_id_name_map = dict(DataSourceDepartment.objects.values_list("id", "name"))
        rel_tree = Tree(DataSourceDepartmentRelation.objects.values_list("department_id", "parent_id"))

        resp_data = []
        for dept in tenant_depts:
            dept_info = {
                "id": dept.id,
                "name": dept.data_source_department.name,
                "extras": dept.data_source_department.extras,
                "category_id": dept.data_source_department.data_source_id,
                "parent": tenant_dept_id_map.get(
                    (dept.data_source_department.department_relation.parent_id, dept.tenant_id)
                ),
                "level": dept.data_source_department.department_relation.level,
                "order": 0,
                "enabled": True,
            }
            # 特殊指定 fields 的情况下仅返回指定的字段
            if fields:
                dept_info = {k: v for k, v in dept_info.items() if k in fields}
                resp_data.append(dept_info)
                continue

            # 没有指定 fields 的时候，额外返回 full_name & children 字段
            dept_full_name = "/".join(
                [
                    dept_id_name_map[x]
                    for x in rel_tree.get_ancestors(dept.data_source_department_id, include_self=True)
                ]
            )
            dept_info["full_name"] = dept_full_name
            dept_info["has_children"] = bool(rel_tree.get_children(dept.data_source_department_id))

            # 若指定 with_ancestors == True，则额外返回祖先 & 孩子部门信息（为什么需要孩子信息？总之老的逻辑是这样的）
            if with_ancestors:
                dept_info["ancestors"] = [
                    {"id": tenant_dept_id_map[(id, dept.tenant_id)], "name": dept_id_name_map.get(id, "--")}
                    for id in rel_tree.get_ancestors(dept.data_source_department_id)
                    if (id, dept.tenant_id) in tenant_dept_id_map
                ]
                children = []
                for child_dept_id in rel_tree.get_children(dept.data_source_department_id):
                    if (child_dept_id, dept.tenant_id) not in tenant_dept_id_map:
                        continue

                    child_dept_name = dept_id_name_map.get(child_dept_id, "--")
                    children.append(
                        {
                            "id": tenant_dept_id_map[(child_dept_id, dept.tenant_id)],
                            "name": child_dept_name,
                            "full_name": f"{dept_full_name}/{child_dept_name}",
                            "has_children": bool(rel_tree.get_children(child_dept_id)),
                        }
                    )

                dept_info["children"] = children

            resp_data.append(dept_info)

        return resp_data

    def _filter_queryset(self, params: Dict[str, Any]) -> QuerySet:
        # 注：兼容 v2 的 OpenAPI 只提供默认租户的数据（包括默认租户本身数据源的数据 & 其他租户协同过来的数据）
        queryset = (
            TenantDepartment.objects.select_related("data_source_department__department_relation")
            .filter(tenant=self.default_tenant, data_source__type=DataSourceTypeEnum.REAL)
            .distinct()
        )
        if not params.get("lookup_field"):
            return queryset

        target_lookups = []
        lookup_field = params["lookup_field"]

        if exact_lookups := params.get("exact_lookups"):
            # 在 DB 中根据 parent 过滤只能使用数据源部门 ID，这里需要特殊转换
            # 注：fuzzy_lookups 不需要特殊转换，原因是 fuzzy_lookups 只支持按 name 查询
            if lookup_field == "parent":
                exact_lookups = TenantDepartment.objects.filter(
                    id__in=exact_lookups,
                ).values_list("data_source_department_id", flat=True)

            target_lookups = [Q(**{self._convert_lookup_field(lookup_field): x}) for x in exact_lookups]
        elif fuzzy_lookups := params.get("fuzzy_lookups"):
            target_lookups = [
                Q(**{f"{self._convert_lookup_field(lookup_field)}__icontains": x}) for x in fuzzy_lookups
            ]

        return queryset.filter(reduce(operator.or_, target_lookups))

    @staticmethod
    def _convert_lookup_field(lookup_field: str) -> str:
        """兼容 API 中 lookup field 字段都是老版本中数据库表字段，但新版本中这些字段分散在多个表中，需要特殊转换"""
        if lookup_field == "id":
            return "id"
        if lookup_field == "name":
            return "data_source_department__name"
        if lookup_field == "category_id":
            return "data_source_department__data_source_id"
        if lookup_field == "parent":
            return "data_source_department__department_relation__parent"
        if lookup_field == "level":
            return "data_source_department__department_relation__level"

        raise error_codes.VALIDATION_ERROR.f(f"unsupported lookup field: {lookup_field}")


class DepartmentRetrieveApi(LegacyOpenApiCommonMixin, DefaultTenantMixin, generics.RetrieveAPIView):
    """查询单个部门"""

    def get(self, request, *args, **kwargs):
        slz = DepartmentRetrieveInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        # 注：兼容 v2 的 OpenAPI 只提供默认租户的数据（包括默认租户本身数据源的数据 & 其他租户协同过来的数据）
        tenant_dept = (
            TenantDepartment.objects.select_related("data_source_department__department_relation")
            .filter(id=kwargs["id"], tenant=self.default_tenant, data_source__type=DataSourceTypeEnum.REAL)
            .first()
        )

        if not tenant_dept:
            raise Http404(f"department {kwargs['id']} not found")

        resp_data = {
            "id": tenant_dept.id,
            "name": tenant_dept.data_source_department.name,
            "extras": tenant_dept.data_source_department.extras,
            "category_id": tenant_dept.data_source_department.data_source_id,
            "enabled": True,
            "order": 0,
        }

        # 当前部门对应的 MPTT 树节点
        dept_relation = tenant_dept.data_source_department.department_relation

        # 如果指定返回字段，则只需要返回对应的字段即可
        if fields := params.get("fields"):
            resp_data = {k: v for k, v in resp_data.items() if k in fields}
            # 由于 parent 需要额外计算，因此特殊分支处理
            if "parent" in fields:
                resp_data["parent"] = self._get_dept_parent_id(tenant_dept, dept_relation)
            # 由于 level 需要额外计算，因此特殊分支处理
            if "level" in fields:
                resp_data["level"] = self._get_dept_tree_level(dept_relation)
            return Response(resp_data)

        # fields 为空时，额外返回字段 full_name（即部门组织路径），has_children（是否拥有子部门）
        # children（子部门信息列表）[{id, name, full_name, has_children}]
        resp_data["parent"] = self._get_dept_parent_id(tenant_dept, dept_relation)
        resp_data["level"] = self._get_dept_tree_level(dept_relation)

        tenant_dept_full_name = self._get_dept_full_name(tenant_dept, dept_relation)
        children = self._get_dept_children(tenant_dept, tenant_dept_full_name)
        resp_data["full_name"] = tenant_dept_full_name
        resp_data["has_children"] = bool(children)
        resp_data["children"] = children

        if params.get("with_ancestors"):
            resp_data["ancestors"] = self._get_dept_ancestors(tenant_dept, dept_relation)

        return Response(resp_data)

    @staticmethod
    def _get_dept_full_name(tenant_dept: TenantDepartment, dept_relation: DataSourceDepartmentRelation) -> str:
        """获取部门组织路径信息"""
        # TODO 协同后续支持指定组织范围的话，不能直接吐出到根部门的路径
        if not dept_relation:
            return tenant_dept.data_source_department.name

        return "/".join(dept_relation.get_ancestors(include_self=True).values_list("department__name", flat=True))

    @staticmethod
    def _get_dept_ancestors(tenant_dept: TenantDepartment, dept_relation: DataSourceDepartmentRelation) -> List[Dict]:
        """获取租户部门的所有祖先部门信息"""
        if not dept_relation:
            return []

        ancestors = [
            {"id": rel.department.id, "name": rel.department.name}
            for rel in dept_relation.get_ancestors(include_self=False).select_related("department")
        ]
        dept_id_map = dict(
            TenantDepartment.objects.filter(
                data_source_department_id__in=[dept["id"] for dept in ancestors], tenant_id=tenant_dept.tenant_id
            ).values_list("data_source_department_id", "id")
        )
        # 如果 dept["id"] 不在 dept_id_map 中，说明该部门未同步成租户部门（可能是协同的部分同步的情况）
        return [
            {"id": dept_id_map[dept["id"]], "name": dept["name"]} for dept in ancestors if dept["id"] in dept_id_map
        ]

    @staticmethod
    def _get_dept_children(tenant_dept: TenantDepartment, dept_full_name: str) -> List[Dict]:
        """获取租户部门子部门信息"""
        child_dept_relations = DataSourceDepartmentRelation.objects.filter(
            parent_id=tenant_dept.data_source_department_id,
        ).select_related("department")

        if not child_dept_relations.exists():
            return []

        grandchild_dept_relations = DataSourceDepartmentRelation.objects.filter(
            parent_id__in=[rel.department_id for rel in child_dept_relations],
        )
        has_grand_child_map = {rel.parent_id: True for rel in grandchild_dept_relations}
        dept_id_map = dict(
            TenantDepartment.objects.filter(
                data_source_department_id__in=[rel.department_id for rel in child_dept_relations],
                tenant_id=tenant_dept.tenant_id,
            ).values_list("data_source_department_id", "id")
        )
        return [
            {
                "id": dept_id_map[rel.department_id],
                "name": rel.department.name,
                "full_name": f"{dept_full_name}/{rel.department.name}",
                "has_children": has_grand_child_map.get(rel.department_id, False),
            }
            for rel in child_dept_relations
            if rel.department_id in dept_id_map
        ]

    @staticmethod
    def _get_dept_parent_id(tenant_dept: TenantDepartment, dept_relation: DataSourceDepartmentRelation) -> int | None:
        """获取租户部门的父部门ID"""
        if not (dept_relation and dept_relation.parent_id):
            return None

        # 父租户部门必须是同租户的
        parent_tenant_dept = TenantDepartment.objects.filter(
            data_source_department_id=dept_relation.parent_id, tenant_id=tenant_dept.tenant_id
        ).first()
        if not parent_tenant_dept:
            return None

        return parent_tenant_dept.id

    @staticmethod
    def _get_dept_tree_level(dept_relation: DataSourceDepartmentRelation) -> int:
        """获取租户部门的树层级"""
        if not dept_relation:
            return 0

        # TODO 协同后续支持指定组织范围的话，返回的应该是伪根到该节点的层级？
        return dept_relation.level


class DepartmentChildrenListApi(LegacyOpenApiCommonMixin, DefaultTenantMixin, generics.ListAPIView):
    """获取某部门的子部门列表"""

    pagination_class = LegacyOpenApiPagination

    def get(self, request, *args, **kwargs):
        # 注：兼容 v2 的 OpenAPI 只提供默认租户的数据（包括默认租户本身数据源的数据 & 其他租户协同过来的数据）
        tenant_dept = TenantDepartment.objects.filter(
            id=kwargs["lookup_value"], tenant=self.default_tenant, data_source__type=DataSourceTypeEnum.REAL
        ).first()
        if not tenant_dept:
            raise Http404(f"department {kwargs['lookup_value']} not found")

        dept_relations = DataSourceDepartmentRelation.objects.filter(
            parent_id=tenant_dept.data_source_department_id,
        ).select_related("department")

        dept_id_map = dict(
            TenantDepartment.objects.filter(
                data_source_department_id__in=[rel.department_id for rel in dept_relations],
                tenant_id=tenant_dept.tenant_id,
            ).values_list("data_source_department_id", "id")
        )

        resp_data = [
            {"id": dept_id_map[dept.department_id], "name": dept.department.name, "order": idx}
            for idx, dept in enumerate(dept_relations, start=1)
            if dept.department_id in dept_id_map
        ]
        return Response(resp_data)


class ProfileDepartmentListApi(LegacyOpenApiCommonMixin, DefaultTenantMixin, generics.ListAPIView):
    """查询单个用户的部门列表"""

    pagination_class = LegacyOpenApiPagination

    def get(self, request, *args, **kwargs):
        slz = ProfileDepartmentListInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        # 注：兼容 v2 的 OpenAPI 只提供默认租户的数据（包括默认租户本身数据源的数据 & 其他租户协同过来的数据）
        lookup_filter = {}
        if params["lookup_field"] == "username":
            # username 其实就是新的租户用户 ID，形式如 admin / admin@qq.com / uuid4
            lookup_filter["id"] = kwargs["lookup_value"]
        else:
            # 用户 ID 即为数据源用户 ID
            lookup_filter["data_source_user__id"] = kwargs["lookup_value"]

        tenant_user = (
            TenantUser.objects.select_related("data_source_user")
            .filter(
                Q(**lookup_filter),
                Q(tenant_id=self.default_tenant.id),
                # Note: 兼容 v2 仅仅允许默认租户下的虚拟账号输出
                Q(data_source__type=DataSourceTypeEnum.REAL)
                | Q(data_source__owner_tenant_id=self.default_tenant.id, data_source__type=DataSourceTypeEnum.VIRTUAL),
            )
            .first()
        )
        if not tenant_user:
            raise Http404(f"user {params['lookup_field']}:{kwargs['lookup_value']} not found")

        with_ancestors = params["with_ancestors"] or params["with_family"]
        return Response(self._get_user_dept_infos(tenant_user, with_ancestors=with_ancestors))

    def _get_user_dept_infos(self, tenant_user: TenantUser, with_ancestors: bool) -> List[Dict]:
        departments = [
            rel.department
            for rel in DataSourceDepartmentUserRelation.objects.filter(
                user=tenant_user.data_source_user,
            )
        ]
        if not departments:
            return []

        dept_id_map = dict(
            TenantDepartment.objects.filter(
                data_source_department__in=departments, tenant_id=tenant_user.tenant_id
            ).values_list("data_source_department_id", "id")
        )
        user_dept_infos = []
        for idx, dept in enumerate(departments, start=1):
            if dept.id not in dept_id_map:
                continue

            dept_info = {
                "id": dept_id_map[dept.id],
                "name": dept.name,
                "full_name": self._get_dept_full_name(dept),
                "order": idx,
            }
            if with_ancestors:
                dept_info["family"] = self._get_dept_ancestors(dept, dept_info["full_name"], tenant_user.tenant_id)

            user_dept_infos.append(dept_info)

        return user_dept_infos

    @staticmethod
    def _get_dept_ancestors(dept: DataSourceDepartment, dept_full_name: str, tenant_id: str) -> List[Dict]:
        """获取某个部门祖先信息"""
        dept_relation = DataSourceDepartmentRelation.objects.filter(department=dept).first()
        if not dept_relation:
            return []

        ancestors = dept_relation.get_ancestors().select_related("department")
        dept_id_map = dict(
            TenantDepartment.objects.filter(
                data_source_department_id__in=[rel.department_id for rel in ancestors], tenant_id=tenant_id
            ).values_list("data_source_department_id", "id")
        )
        ancestor_count = ancestors.count()
        return [
            {
                "id": dept_id_map[dept.department_id],
                "name": dept.department.name,
                "full_name": dept_full_name.rsplit("/", ancestor_count - idx + 1)[0],
                "order": idx,
            }
            for idx, dept in enumerate(ancestors, start=1)
            if dept.department_id in dept_id_map
        ]

    @staticmethod
    def _get_dept_full_name(dept: DataSourceDepartment) -> str:
        """获取部门组织路径信息"""
        dept_relation = DataSourceDepartmentRelation.objects.filter(department=dept).first()
        if not dept_relation:
            return dept.name

        # TODO 协同后续支持指定组织范围的话，不能直接吐出到根部门的路径
        return "/".join(dept_relation.get_ancestors(include_self=True).values_list("department__name", flat=True))
