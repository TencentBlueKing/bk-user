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

from functools import cached_property

from apigw_manager.drf.authentication import ApiGatewayJWTAuthentication
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource


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
