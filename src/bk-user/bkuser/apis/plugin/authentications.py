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


from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed


class InnerPluginAuthentication(BasicAuthentication):
    """对于用户管理内部插件 API 调用，使用特定的内部认证标识"""

    def authenticate(self, request):
        auth_token = request.META.get("HTTP_X_INTERNAL_CALL")

        if not auth_token:
            raise AuthenticationFailed("Missing required authentication header: X-Internal-Call.")

        if auth_token != settings.INTERNAL_PLUGIN_API_TOKEN:
            raise AuthenticationFailed("Invalid internal authentication token.")

        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(
            username="admin", defaults={"is_active": True, "is_staff": False, "is_superuser": False}
        )
        return user, None
