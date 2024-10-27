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
from typing import Dict

from django.conf import settings
from django.views.generic import View

from bklogin.authentication.manager import BkTokenManager
from bklogin.component.bk_user import api as bk_user_api

from .constants import CompatibilityApiErrorCodeEnum
from .mixins import CompatibilityApiMixin


class TokenIntrospectCompatibilityApi(View, CompatibilityApiMixin):
    """Token 解析"""

    def get(self, request, *args, **kwargs):
        bk_token = request.GET.get(settings.BK_TOKEN_COOKIE_NAME)

        ok, username, msg = BkTokenManager().is_valid(bk_token)
        if not ok:
            return self.fail_response(error_code=CompatibilityApiErrorCodeEnum.PARAM_NOT_VALID, message=msg)

        return self.ok_response(data={self.username_key: username})


class UserRetrieveCompatibilityApi(View, CompatibilityApiMixin):
    """通过 Token 获取用户"""

    def get(self, request, *args, **kwargs):
        bk_token = request.GET.get(settings.BK_TOKEN_COOKIE_NAME)

        ok, username, msg = BkTokenManager().is_valid(bk_token)
        if not ok:
            # 对于来着 ESB 请求，如果 bk_token 验证不通过，还可以通过 username 参数指定查询的用户
            username = request.GET.get(self.username_key)
            if not (self.is_request_from_esb(request) and username):
                return self.fail_response(error_code=CompatibilityApiErrorCodeEnum.PARAM_NOT_VALID, message=msg)

        # 通过用户管理查询用户信息
        user = bk_user_api.get_tenant_user(username)

        # Note: 与 self.username_key 不一样，区别在于 v3 API, 其 is_login 放回 bk_username, get_user 返回 username
        username_key = "bk_username" if self.api_version == "v2" else "username"
        user_info: Dict[str, int | str] = {
            # bk_username / username
            username_key: user.id,
            # 基本信息
            "language": user.language,
            "time_zone": user.time_zone,
            # 多租户版本新增
            "tenant_id": user.tenant_id,
            "full_name": user.full_name,  # 姓名
            "display_name": user.display_name,  # 统一展示名
            # ----- 兼容 ------
            # 兼容数据
            "chname": user.full_name,
            # 【兼容】固定或空值返回
            "qq": "",
            "phone": "",
            "email": "",
            "wx_userid": "",
        }
        # 角色已废弃，这里只是兼容处理
        role_key = "bk_role" if self.api_version == "v2" else "role"
        user_info[role_key] = "0" if self.api_version == "v1" else 0

        return self.ok_response(data=user_info)
