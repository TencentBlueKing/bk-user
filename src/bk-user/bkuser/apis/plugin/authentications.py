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


from django.contrib.auth import get_user_model
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed


class InnerPluginAuthentication(BasicAuthentication):
    """对于用户管理内部插件调用，使用特定的内部认证标识"""

    def authenticate(self, request):
        # 检查是否为内部插件调用（通过特定的请求头标识）
        if not request.META.get("HTTP_X_INTERNAL_CALL") == "bk-user-plugin":
            raise AuthenticationFailed("Invalid authentication header X-Internal-Call.")

        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(
            username="admin", defaults={"is_active": True, "is_staff": False, "is_superuser": False}
        )
        return user, None
