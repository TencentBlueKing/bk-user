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
from django.conf import settings
from rest_framework.permissions import BasePermission

from bkuser.apps.tenant.constants import BuiltInTenantIDEnum


class IsCurrentUserTenant(BasePermission):
    """校验 X-Bk-Tenant-Id 请求头是否为当前登录用户所属租户，防止跨租户访问"""

    message = "X-Bk-Tenant-Id header does not match the tenant of current user"

    def has_permission(self, request, view):
        # 用户所属租户由 ApiGatewayJWTAuthentication 认证时从 JWT user.tenant_id 写入
        # （见 apigw_manager UserModelBackend），多租户模式下必须存在
        user_tenant_id = getattr(request.user, "tenant_id", "")
        # 单租户模式下网关可能不下发用户租户，此时只存在默认租户
        if not user_tenant_id and not settings.ENABLE_MULTI_TENANT_MODE:
            user_tenant_id = BuiltInTenantIDEnum.DEFAULT

        # 单租户模式下 TenantIDHeaderMiddleware 已将该请求头强制改写为默认租户，与上面的兜底值一致
        header_tenant_id = request.META.get("HTTP_X_BK_TENANT_ID")
        return bool(user_tenant_id) and header_tenant_id == user_tenant_id
