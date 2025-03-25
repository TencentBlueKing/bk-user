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

from django.conf import settings
from django.utils.translation import override
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from bkuser.apis.apigw.authentications import InnerBearerTokenAuthentication
from bkuser.apis.apigw.permissions import IsInnerBearerTokenAuthenticated


class InnerApiCommonMixin:
    authentication_classes = [InnerBearerTokenAuthentication]
    permission_classes = [IsInnerBearerTokenAuthenticated]

    request: Request

    TenantHeaderKey = "HTTP_X_BK_TENANT_ID"

    @cached_property
    def tenant_id(self) -> str:
        tenant_id = self.request.META.get(self.TenantHeaderKey)

        if not tenant_id:
            raise ValidationError("X-Bk-Tenant-Id header is required")

        return tenant_id

    def dispatch(self, request, *args, **kwargs):
        # 若请求未携带语言信息，则默认使用英文
        if not request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME):
            with override("en-us"):
                return super().dispatch(request, *args, **kwargs)  # type: ignore
        return super().dispatch(request, *args, **kwargs)  # type: ignore
