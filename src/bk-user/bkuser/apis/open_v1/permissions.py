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

from rest_framework.permissions import BasePermission


class IsAllowedAppCode(BasePermission):
    """
    仅允许配置好的 AppCode
    需要配合 ESBAuthentication 一起使用
    """

    def has_permission(self, request, view):
        """
        目前只允许桌面访问
        桌面 AppCode: https://github.com/TencentBlueKing/blueking-console/blob/7ab1efb189deeed2e95557cd9a90d62c1b4b7735/backend/components/esb.py#L35
        """
        return hasattr(request, "bk_app_code") and request.bk_app_code in ["bk_paas"]
