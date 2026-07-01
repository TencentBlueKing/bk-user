# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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
from functools import cached_property
from typing import List

from apigw_manager.drf.authentication import ApiGatewayJWTAuthentication
from django.utils.decorators import method_decorator
from django.utils.translation import override
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from bkuser.apps.data_source.cache import DataSourceCache

from .permissions import ApiGatewayAppVerifiedPermission


class OpenApiCommonMixin:
    authentication_classes = [ApiGatewayJWTAuthentication]
    permission_classes = [ApiGatewayAppVerifiedPermission]

    request: Request

    TenantHeaderKey = "HTTP_X_BK_TENANT_ID"

    @cached_property
    def tenant_id(self) -> str:
        tenant_id = self.request.META.get(self.TenantHeaderKey)

        if not tenant_id:
            raise ValidationError("X-Bk-Tenant-Id header is required")

        return tenant_id

    @cached_property
    def real_data_source_ids(self) -> List[int]:
        """本租户拥有的 REAL 数据源 ID，基于全局缓存避免 DB 查询"""
        return list(DataSourceCache.real_ids_by_owner(self.tenant_id))

    @cached_property
    def virtual_data_source_id(self) -> int:
        """本租户的虚拟数据源 ID，不存在时返回 0，基于全局缓存避免 DB 查询"""
        return DataSourceCache.virtual_id_by_owner(self.tenant_id)

    # 将 API 响应内容的默认语言设置为英文
    @method_decorator(override("en-us"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)  # type: ignore
