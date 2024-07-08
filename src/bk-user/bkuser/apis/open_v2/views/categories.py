# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.db.models import QuerySet
from rest_framework import generics
from rest_framework.response import Response

from bkuser.apis.open_v2.mixins import DefaultTenantMixin, LegacyOpenApiCommonMixin
from bkuser.apis.open_v2.pagination import LegacyOpenApiPagination
from bkuser.apis.open_v2.serializers.categories import CategoriesListInputSLZ, CategoriesListOutputSLZ
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.tenant.models import Tenant, TenantUserIDGenerateConfig


class CategoriesListApi(LegacyOpenApiCommonMixin, DefaultTenantMixin, generics.ListAPIView):
    pagination_class = LegacyOpenApiPagination

    def get_queryset(self) -> QuerySet[DataSource]:
        return self.get_real_user_data_sources()

    def get(self, request, *args, **kwargs):
        slz = CategoriesListInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        data_sources = self.get_queryset()

        data_source_domain_map = {
            cfg.data_source_id: cfg.domain
            for cfg in TenantUserIDGenerateConfig.objects.filter(data_source__in=data_sources)
        }

        tenant_name_map = dict(Tenant.objects.values_list("id", "name"))
        categories = [
            {
                "id": ds.id,
                # 由于新版本中，单个租户只会有一个数据源，因此这里以租户名称作为数据源名称
                "display_name": tenant_name_map[ds.owner_tenant_id],
                # 如果没有特殊指定，由于 domain 字段是 unique 的，因此应该是 None 而非 ""
                "domain": data_source_domain_map.get(ds.id),
                "default": ds.owner_tenant_id == self.default_tenant.id,
                "status": "normal",
                "enabled": True,
            }
            for ds in data_sources
        ]
        if slz.validated_data["no_page"]:
            return Response(CategoriesListOutputSLZ(categories, many=True).data)

        return self.get_paginated_response(CategoriesListOutputSLZ(self.paginate_queryset(categories), many=True).data)
