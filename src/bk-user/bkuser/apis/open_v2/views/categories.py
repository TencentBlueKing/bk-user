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
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser.apis.open_v2.mixins import OpenApiAccessControlMixin
from bkuser.apis.open_v2.serializers import CategoriesListInputSLZ, CategoriesListOutputSLZ
from bkuser.apps.data_source.constants import DataSourceStatus, TenantUserIdRuleEnum
from bkuser.apps.data_source.models import DataSource


class CategoriesListApi(OpenApiAccessControlMixin, generics.ListAPIView):
    queryset = DataSource.objects.all()

    @swagger_auto_schema(
        tags=["open_v2.categories"],
        operation_description="查询目录列表",
        responses={status.HTTP_200_OK: CategoriesListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        slz = CategoriesListInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        categories = [
            {
                # TODO 支持租户协同后，因为协同产生的目录也要添加进来，但是其目录 ID 就不能是数据源的 ID
                "id": ds.id,
                "display_name": ds.name,
                "domain": ds.domain,
                # 历史数据迁移后，只有默认目录的租户用户 ID 生成规则是 username
                "default": bool(ds.owner_tenant_user_id_rule == TenantUserIdRuleEnum.USERNAME),
                "status": ds.status,
                "enabled": bool(ds.status == DataSourceStatus.ENABLED),
            }
            for ds in self.get_queryset()
        ]
        if slz.validated_data["no_page"]:
            return Response(CategoriesListOutputSLZ(categories, many=True).data)

        return self.get_paginated_response(CategoriesListOutputSLZ(self.paginate_queryset(categories), many=True).data)
