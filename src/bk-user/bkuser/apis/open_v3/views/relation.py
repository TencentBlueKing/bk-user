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
from bkuser.apis.open_v3.serializers.relation import TenantDepartmentUserRelationListOutputSLZ
from bkuser.apps.data_source.models import DataSourceDepartmentUserRelation
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
        # 获取本租户下所有实名数据源用户 ID
        data_source_user_ids = TenantUser.objects.filter(
            tenant_id=self.tenant_id, data_source_id=self.real_data_source_id
        ).values_list("data_source_user_id", flat=True)

        # 获取数据源用户与部门间关系并分页
        relations = DataSourceDepartmentUserRelation.objects.filter(
            data_source_id=self.real_data_source_id, user_id__in=data_source_user_ids
        ).order_by("id")
        page = self.paginate_queryset(relations)

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
        results = []
        for rel in page:
            tenant_user_id = user_id_map.get(rel.user_id)
            tenant_dept_id = dept_id_map.get(rel.department_id)
            results.append(
                {
                    "bk_username": tenant_user_id,
                    "department_id": tenant_dept_id,
                }
            )

        return self.get_paginated_response(TenantDepartmentUserRelationListOutputSLZ(results, many=True).data)
