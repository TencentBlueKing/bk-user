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
from bklogin.common.error_codes import error_codes


class APIGatewayAppVerifiedMixin:
    """校验来源 APIGateway JWT 的应用是否认证"""

    # FIXME (nan): 待讨论清楚网关本身的用户认证与登录如何认证后再去除
    skip_app_verified = False

    def dispatch(self, request, *args, **kwargs):
        if self.skip_app_verified:
            return super().dispatch(request, *args, **kwargs)  # type: ignore

        app = getattr(request, "app", None)
        if app and app.verified:
            return super().dispatch(request, *args, **kwargs)  # type: ignore

        raise error_codes.UNAUTHENTICATED.f("the api must be verify app from api gateway")
