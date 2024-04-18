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
from functools import reduce
from typing import Dict, List, Set

from django.db.models import Q, QuerySet
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apis.web.organization.serializers import (
    TenantUserSearchInputSLZ,
    TenantUserSearchOutputSLZ,
)
from bkuser.apps.data_source.models import DataSourceDepartmentRelation, DataSourceDepartmentUserRelation
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.models import Tenant, TenantUser


class TenantUserSearchApi(CurrentUserTenantMixin, generics.ListAPIView):
    """搜索租户用户"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    pagination_class = None
    # 限制搜索结果，只提供前 20 条记录，如果展示不完全，需要用户细化搜索条件
    search_limit = 20

    def get_queryset(self) -> QuerySet[TenantUser]:
        slz = TenantUserSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        keyword = slz.validated_data["keyword"]

        # FIXME (su) 手机 & 邮箱过滤在 DB 加密后不可用，到时候再调整
        return (
            TenantUser.objects.filter(tenant_id=self.get_current_tenant_id())
            .filter(
                Q(data_source_user__username__icontains=keyword)
                | Q(data_source_user__full_name__icontains=keyword)
                | Q(data_source_user__email__icontains=keyword)
                | Q(data_source_user__phone__icontains=keyword)
            )
            .select_related("data_source_user")[: self.search_limit]
        )

    def _get_user_organization_paths_map(self, tenant_users: QuerySet[TenantUser]) -> Dict[str, List[str]]:
        """获取租户部门的组织路径信息"""
        data_source_user_ids = [tenant_user.data_source_user_id for tenant_user in tenant_users]

        # 数据源用户 ID -> [数据源部门 ID1， 数据源部门 ID2]
        user_dept_id_map = defaultdict(list)
        for relation in DataSourceDepartmentUserRelation.objects.filter(user_id__in=data_source_user_ids):
            user_dept_id_map[relation.user_id].append(relation.department_id)

        # 数据源部门 ID 集合
        data_source_dept_ids: Set[int] = reduce(
            lambda x, y: x | y, [set(ids) for ids in user_dept_id_map.values()], set()
        )

        # 数据源部门 ID -> 组织路径
        org_path_map = {}
        for dept_relation in DataSourceDepartmentRelation.objects.filter(
            department_id__in=data_source_dept_ids
        ).select_related("department"):
            dept_names = list(
                dept_relation.get_ancestors(include_self=True).values_list("department__name", flat=True)
            )
            org_path_map[dept_relation.department_id] = "/".join(dept_names)

        # 租户用户 ID -> 组织路径列表
        return {
            user.id: [org_path_map.get(dept_id, "") for dept_id in user_dept_id_map.get(user.data_source_user_id, [])]
            for user in tenant_users
        }

    @swagger_auto_schema(
        tags=["organization"],
        operation_description="搜索租户用户",
        query_serializer=TenantUserSearchInputSLZ(),
        responses={status.HTTP_200_OK: TenantUserSearchOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        tenant_users = self.get_queryset()
        context = {
            "tenant_name_map": {tenant.id: tenant.name for tenant in Tenant.objects.all()},
            "org_path_map": self._get_user_organization_paths_map(tenant_users),
        }
        resp_data = TenantUserSearchOutputSLZ(tenant_users, many=True, context=context).data
        return Response(resp_data, status=status.HTTP_200_OK)
