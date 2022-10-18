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
# from django.conf import settings
from rest_framework import permissions

# import bkuser_sdk
# from .constants import RoleCodeEnum
# from bkuser_shell.common.core_client import get_api_client


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


# def is_superuser(username):

#     if not username:
#         return False

#     if username in settings.INIT_SUPERUSER_NAMES:
#         # 白名单直接返回
#         return True

#     # TODO: change to get by requests
#     api_instance = bkuser_sdk.ProfilesApi(get_api_client())
#     profile = api_instance.v2_profiles_read(lookup_value=username)

#     # 由其他系统写入
#     return profile.role == RoleCodeEnum.SUPERUSER
