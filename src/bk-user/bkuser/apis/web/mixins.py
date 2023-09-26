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
from rest_framework.request import Request

from bkuser.common.error_codes import error_codes


class CurrentUserTenantMixin:
    """当前用户所属租户"""

    request: Request

    def get_current_tenant_id(self) -> str:
        """
        获取当前登录用户所属租户的ID
        """
        tenant_id = self.request.user.get_property("tenant_id")
        if not tenant_id:
            raise error_codes.GET_CURRENT_TENANT_FAILED

        return tenant_id
