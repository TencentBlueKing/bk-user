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
from django.conf import settings
from django.http import HttpResponseForbidden
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.tenant.constants import CollaborationStrategyStatus
from bkuser.apps.tenant.models import CollaborationStrategy


class OpenWebApiCommonMixin:
    authentication_classes = [ApiGatewayJWTAuthentication]
    permission_classes = [IsAuthenticated]

    request: Request

    TenantHeaderKey = "HTTP_X_BK_TENANT_ID"

    def dispatch(self, request, *args, **kwargs):
        # 校验浏览器请求
        if not self._is_browser_request(request):
            return HttpResponseForbidden("OpenWeb APIs are only allowed from browser requests")

        return super().dispatch(request, *args, **kwargs)  # type: ignore

    def _is_browser_request(self, request) -> bool:
        """校验是否为浏览器请求"""
        http_sec_fetch_headers = {"HTTP_SEC_FETCH_DEST", "HTTP_SEC_FETCH_MODE", "HTTP_SEC_FETCH_SITE"}
        is_https = settings.BK_DOMAIN_SCHEME == "https"

        # http 协议下不需要校验 sec-fetch-* 请求头
        required_headers = [
            h for h in settings.OPEN_WEB_API_REQUIRED_BROWSER_HEADERS if is_https or h not in http_sec_fetch_headers
        ]

        # 校验必要请求头存在且值为非空
        if not all(request.META.get(key) for key in required_headers):
            return False

        # 校验 User-Agent 是否在白名单中
        if "HTTP_USER_AGENT" in required_headers:
            user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
            if not any(browser.lower() in user_agent for browser in settings.OPEN_WEB_API_USER_AGENT_WHITELIST):
                return False

        # https 协议下校验 Sec-Fetch-* 请求头的值
        if is_https:
            sec_fetch_rules = {
                "HTTP_SEC_FETCH_DEST": {"empty"},
                "HTTP_SEC_FETCH_MODE": {"cors", "same-origin"},
                "HTTP_SEC_FETCH_SITE": {"same-site", "same-origin"},
            }
            for header, valid_values in sec_fetch_rules.items():
                if header in required_headers and request.META.get(header) not in valid_values:
                    return False

        return True

    @cached_property
    def tenant_id(self) -> str:
        tenant_id = self.request.META.get(self.TenantHeaderKey)

        if not tenant_id:
            raise ValidationError("X-Bk-Tenant-Id header is required")

        return tenant_id

    @cached_property
    def real_data_source_ids(self) -> List[int]:
        return list(
            DataSource.objects.filter(owner_tenant_id=self.tenant_id, type=DataSourceTypeEnum.REAL).values_list(
                "id", flat=True
            )
        )

    @cached_property
    def collaboration_data_source_ids(self) -> List[int]:
        collaboration_tenant_ids = list(
            CollaborationStrategy.objects.filter(target_tenant_id=self.tenant_id)
            .exclude(target_status=CollaborationStrategyStatus.UNCONFIRMED)
            .values_list("source_tenant_id", flat=True)
        )

        if not collaboration_tenant_ids:
            return []
        return list(
            DataSource.objects.filter(
                owner_tenant_id__in=collaboration_tenant_ids, type=DataSourceTypeEnum.REAL
            ).values_list("id", flat=True)
        )

    @cached_property
    def virtual_data_source_id(self) -> int:
        # 虚拟数据源不存在时，返回 0
        data_source = (
            DataSource.objects.filter(owner_tenant_id=self.tenant_id, type=DataSourceTypeEnum.VIRTUAL)
            .only("id")
            .first()
        )
        if not data_source:
            return 0

        return data_source.id
