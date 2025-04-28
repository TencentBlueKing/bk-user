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
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status

from bkuser.apis.open_v3.mixins import OpenApiCommonMixin
from bkuser.apis.open_v3.serializers.relation import (
    TenantDepartmentRelationListOutputSLZ,
    TenantDepartmentUserRelationListOutputSLZ,
    TenantUserLeaderRelationListOutputSLZ,
)
from bkuser.apps.data_source.models import (
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.tenant.models import TenantDepartment, TenantUser


class TenantDepartmentUserRelationListApi(OpenApiCommonMixin, generics.ListAPIView):
    """
    查询部门用户关系
    """

    @swagger_auto_schema(
        tags=["open_v3.relation"],
        operation_id="list_department_user_relation",
        operation_description="查询部门用户关系",
        responses={status.HTTP_200_OK: TenantDepartmentUserRelationListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        # 获取数据源用户与部门间关系并分页
        relations = DataSourceDepartmentUserRelation.objects.filter(data_source_id=self.real_data_source_id).order_by(
            "id"
        )
        page = self.paginate_queryset(relations)

        # 获取所有相关的数据源用户 ID 和部门 ID
        user_ids = {rel.user_id for rel in page}
        dept_ids = {rel.department_id for rel in page}

        # 获取数据源用户与租户用户之间的映射
        user_id_map = dict(
            TenantUser.objects.filter(data_source_user_id__in=user_ids, tenant_id=self.tenant_id).values_list(
                "data_source_user_id", "id"
            )
        )

        # 获取数据源部门与租户部门之间的映射
        dept_id_map = dict(
            TenantDepartment.objects.filter(
                data_source_department_id__in=dept_ids, tenant_id=self.tenant_id
            ).values_list("data_source_department_id", "id")
        )

        # 构建当前页的结果
        # TODO: 由于数据源同步过程存在两阶段：
        # 1.外部数据源同步到数据源用户（部门）2.数据源用户（部门）同步到租户用户（部门）
        # 所以可能存在数据源用户（部门）存在，而租户用户（部门）不存在的情况
        # 但是出现这种情况概率较低，后续考虑如何处理
        results = [
            {
                "bk_username": user_id_map[rel.user_id],
                "department_id": dept_id_map[rel.department_id],
            }
            for rel in page
        ]

        return self.get_paginated_response(TenantDepartmentUserRelationListOutputSLZ(results, many=True).data)


class TenantDepartmentRelationListApi(OpenApiCommonMixin, generics.ListAPIView):
    """
    查询部门间关系
    """

    @swagger_auto_schema(
        tags=["open_v3.relation"],
        operation_id="list_department_relation",
        operation_description="查询部门间关系",
        responses={status.HTTP_200_OK: TenantDepartmentRelationListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        # 获取数据源部门间的关系并分页
        # Note: 这里为什么没有使用 order_by 保证分页稳定？
        # 因为数据源部门采用 MPTT 模型，Manager 中的 get_queryset 方法已定义按照 tree_id 与 lft 联合排序保证分页稳定性
        relations = DataSourceDepartmentRelation.objects.filter(data_source_id=self.real_data_source_id)
        page = self.paginate_queryset(relations)

        dept_ids = {rel.department_id for rel in page}

        # 获取数据源部门与租户部门之间的映射
        dept_id_map = dict(
            TenantDepartment.objects.filter(
                data_source_department_id__in=dept_ids, tenant_id=self.tenant_id
            ).values_list("data_source_department_id", "id")
        )

        # 构建当前页的结果
        # TODO: 由于数据源同步过程存在两阶段：
        # 1.外部数据源同步到数据源用户（部门）2.数据源用户（部门）同步到租户用户（部门）
        # 所以可能存在数据源部门存在，而租户部门不存在的情况
        # 但是出现这种情况概率较低，后续考虑如何处理
        results = [{"id": dept_id_map[rel.department_id], "parent_id": dept_id_map.get(rel.parent_id)} for rel in page]

        return self.get_paginated_response(TenantDepartmentRelationListOutputSLZ(results, many=True).data)


class TenantUserLeaderRelationListApi(OpenApiCommonMixin, generics.ListAPIView):
    """
    查询用户与 Leader 间关系
    """

    @swagger_auto_schema(
        tags=["open_v3.relation"],
        operation_id="list_user_leader_relation",
        operation_description="查询用户与 Leader 间关系",
        responses={status.HTTP_200_OK: TenantUserLeaderRelationListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        # 获取数据源用户与 Leader 间关系并分页
        relations = DataSourceUserLeaderRelation.objects.filter(data_source_id=self.real_data_source_id).order_by("id")
        page = self.paginate_queryset(relations)

        # 获取所有相关的数据源用户与 Leader ID
        user_ids = {rel.user_id for rel in page}
        leader_ids = {rel.leader_id for rel in page}

        # 获取数据源用户与租户用户之间的映射
        user_id_map = dict(
            TenantUser.objects.filter(
                data_source_user_id__in=user_ids | leader_ids, tenant_id=self.tenant_id
            ).values_list("data_source_user_id", "id")
        )

        # 构建当前页的结果
        # TODO: 由于数据源同步过程存在两阶段：
        # 1.外部数据源同步到数据源用户（部门）2.数据源用户（部门）同步到租户用户（部门）
        # 所以可能存在数据源用户存在，而租户用户不存在的情况
        # 但是出现这种情况概率较低，后续考虑如何处理
        results = [
            {
                "bk_username": user_id_map[rel.user_id],
                "leader_bk_username": user_id_map[rel.leader_id],
            }
            for rel in page
        ]

        return self.get_paginated_response(TenantUserLeaderRelationListOutputSLZ(results, many=True).data)
