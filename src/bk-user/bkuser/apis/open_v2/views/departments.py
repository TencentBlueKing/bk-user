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

from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser.apis.open_v2.mixins import LegacyOpenApiCommonMixin
from bkuser.apis.open_v2.pagination import LegacyOpenApiPagination
from bkuser.apis.open_v2.serializers.departments import DepartmentRetrieveInputSLZ, ProfileDepartmentListInputSLZ
from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
)
from bkuser.apps.tenant.models import TenantDepartment, TenantUser


class DepartmentListApi(LegacyOpenApiCommonMixin, generics.ListAPIView):
    queryset = TenantDepartment.objects.all()
    pagination_class = LegacyOpenApiPagination

    @swagger_auto_schema(
        tags=["open_v2.departments"],
        operation_description="查询部门列表",
        responses={status.HTTP_200_OK: "TODO"},
    )
    def get(self, request, *args, **kwargs):
        return Response("TODO")


class DepartmentRetrieveApi(LegacyOpenApiCommonMixin, generics.RetrieveAPIView):
    """查询单个部门"""

    def get(self, request, *args, **kwargs):
        slz = DepartmentRetrieveInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        # TODO (su) 支持软删除后，需要根据 include_disabled 参数判断是返回被删除的部门还是 Raise 404
        tenant_dept = TenantDepartment.objects.select_related("data_source_department").filter(id=kwargs["id"]).first()
        if not tenant_dept:
            raise Http404

        # 如果指定返回字段，则只需要返回对应的字段即可
        resp_data = {
            "id": tenant_dept.id,
            "name": tenant_dept.data_source_department.name,
            "extras": tenant_dept.data_source_department.extras,
            # TODO 支持协同后不一定是数据源 ID
            "category_id": tenant_dept.data_source_department.data_source_id,
            # TODO 支持软删除后不一定是 True
            "enabled": True,
        }

        # 当前部门对应的 MPTT 树节点
        dept_relation = DataSourceDepartmentRelation.objects.filter(
            department_id=tenant_dept.data_source_department_id,
        ).first()

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

        if params.get("with_ancestors"):
            resp_data["ancestors"] = self._get_dept_ancestors(tenant_dept, dept_relation)

        tenant_dept_full_name = self._get_dept_full_name(dept_relation)
        children = self._get_dept_children(tenant_dept, tenant_dept_full_name)
        resp_data["full_name"] = tenant_dept_full_name
        resp_data["has_children"] = bool(children)
        resp_data["children"] = children
        return Response(resp_data)

    @staticmethod
    def _get_dept_full_name(dept_relation: DataSourceDepartmentRelation) -> str:
        """获取部门组织路径信息"""
        # TODO 考虑协同的情况，不能直接吐出到根部门的路径
        if not dept_relation:
            return ""

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
    def _get_dept_children(tenant_dept: TenantDepartment, parent_dept_full_name: str) -> List[Dict]:
        """获取租户部门子部门信息"""
        dept_relations = DataSourceDepartmentRelation.objects.filter(
            parent_id=tenant_dept.data_source_department_id,
        ).select_related("department")

        if not dept_relations.exists():
            return []

        sub_dept_relations = DataSourceDepartmentRelation.objects.filter(
            parent_id__in=[rel.department_id for rel in dept_relations],
        )
        sub_children_map = defaultdict(list)
        for rel in sub_dept_relations:
            sub_children_map[rel.parent_id].append(rel.department_id)

        dept_id_map = dict(
            TenantDepartment.objects.filter(
                data_source_department_id__in=[rel.department_id for rel in dept_relations],
            ).values_list("data_source_department_id", "id")
        )
        return [
            {
                "id": dept_id_map[rel.department_id],
                "name": rel.department.name,
                "full_name": f"{parent_dept_full_name}/{rel.department.name}",
                "has_children": bool(sub_children_map.get(rel.department_id, [])),
            }
            for rel in dept_relations
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

        # TODO 考虑协同的情况，返回的应该是伪根到该节点的层级？
        return dept_relation.level


class DepartmentChildrenListApi(LegacyOpenApiCommonMixin, generics.ListAPIView):
    pagination_class = LegacyOpenApiPagination

    def get(self, request, *args, **kwargs):
        # TODO (su) 支持软删除后，需要根据 include_disabled 参数判断是返回被删除的部门还是 Raise 404?
        tenant_dept = TenantDepartment.objects.filter(id=kwargs["lookup_value"]).first()
        if not tenant_dept:
            raise Http404

        dept_relations = DataSourceDepartmentRelation.objects.filter(
            parent_id=tenant_dept.data_source_department_id,
        ).select_related("department")

        resp_data = [
            {"id": dept.department_id, "name": dept.department.name, "order": idx}
            for idx, dept in enumerate(dept_relations)
        ]
        return Response(resp_data)


class ProfileDepartmentListApi(LegacyOpenApiCommonMixin, generics.ListAPIView):
    """查询单个用户的部门列表"""

    pagination_class = LegacyOpenApiPagination

    def get(self, request, *args, **kwargs):
        slz = ProfileDepartmentListInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        # TODO (su) 支持软删除后需要根据 include_disabled 参数修改 filters
        if params["lookup_field"] == "username":
            # username 其实就是新的租户用户 ID，形式如 admin / admin@qq.com / uuid4
            filters = {"id": kwargs["lookup_value"]}
        else:
            # TODO 目前 ID 指的是数据源用户 ID，未来支持协同之后，需要重新考虑
            filters = {"data_source_user__id": kwargs["lookup_value"]}

        tenant_user = TenantUser.objects.select_related("data_source_user").filter(**filters).first()
        if not tenant_user:
            raise Http404

        if params["with_ancestors"] or params["with_family"]:
            return Response(self._get_user_dept_infos(tenant_user, with_ancestors=True))

        return Response(self._get_user_dept_infos(tenant_user, with_ancestors=False))

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
        for idx, dept in enumerate(departments):
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
                "full_name": dept_full_name.rsplit("/", ancestor_count - idx)[0],
                "order": idx,
            }
            for idx, dept in enumerate(ancestors)
            if dept.department_id in dept_id_map
        ]

    @staticmethod
    def _get_dept_full_name(dept: DataSourceDepartment) -> str:
        """获取部门组织路径信息"""
        dept_relation = DataSourceDepartmentRelation.objects.filter(department=dept).first()
        if not dept_relation:
            return ""

        # TODO 考虑协同的情况，不能直接吐出到根部门的路径
        return "/".join(dept_relation.get_ancestors(include_self=True).values_list("department__name", flat=True))
