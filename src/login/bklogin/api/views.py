# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS
Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.views.generic import View

from bklogin.api.constants import ApiErrorCodeEnum, ApiErrorCodeEnumV2, ApiErrorCodeEnumV3
from bklogin.api.permissions import verify_permission_of_access_app
from bklogin.api.utils import (
    APIV1FailJsonResponse,
    APIV1OKJsonResponse,
    APIV2FailJsonResponse,
    APIV2OKJsonResponse,
    APIV3FailJsonResponse,
    APIV3OKJsonResponse,
    is_request_from_esb,
)
from bklogin.bkauth.utils import validate_bk_token
from bklogin.common import usermgr

########
#  v1  #
########


class CheckLoginView(View):
    def get(self, request):
        # 验证Token参数
        is_valid, username, message = validate_bk_token(request.GET)
        if not is_valid:
            return APIV1FailJsonResponse(message, code=ApiErrorCodeEnum.PARAM_NOT_VALID.value)
        return APIV1OKJsonResponse("user authentication succeeded", data={"username": username})


class UserView(View):
    def get(self, request):
        """
        获取用户信息API
        """
        # 验证Token参数
        is_valid, username, message = validate_bk_token(request.GET)
        if not is_valid:
            # 如果是ESB的请求，可以直接从参数中获取用户id
            is_from_esb = is_request_from_esb(request)
            username = request.GET.get("username")
            if not is_from_esb or not username:
                return APIV1FailJsonResponse(message, code=ApiErrorCodeEnum.PARAM_NOT_VALID.value)

        # 获取用户数据
        ok, message, data = usermgr.get_user(username)
        if not ok:
            return APIV1FailJsonResponse(message, code=ApiErrorCodeEnum.USER_NOT_EXISTS2.value)

        return APIV1OKJsonResponse("get user information succeeded", data=data)


########
#  v2  #
########


class CheckLoginViewV2(View):
    def get(self, request):
        # 验证Token参数
        is_valid, username, message = validate_bk_token(request.GET)
        if not is_valid:
            return APIV2FailJsonResponse(message, code=ApiErrorCodeEnumV2.PARAM_NOT_VALID.value)

        # bk_token有效情况下，鉴权用户是否有应用访问权限
        is_allowed, message = verify_permission_of_access_app(request, username)
        if not is_allowed:
            return APIV2FailJsonResponse(message, code=ApiErrorCodeEnumV2.ACCESS_PERMISSION_DENIED.value)

        return APIV2OKJsonResponse("user authentication succeeded", data={"bk_username": username})


class UserViewV2(View):
    def get(self, request):
        """
        获取用户信息API
        """
        # 验证Token参数
        is_valid, username, message = validate_bk_token(request.GET)
        if not is_valid:
            # 如果是ESB的请求，可以直接从参数中获取用户id
            is_from_esb = is_request_from_esb(request)
            username = request.GET.get("bk_username")
            if not is_from_esb or not username:
                return APIV2FailJsonResponse(message, code=ApiErrorCodeEnumV2.PARAM_NOT_VALID.value)
        else:
            # bk_token有效情况下，鉴权用户是否有应用访问权限
            is_allowed, message = verify_permission_of_access_app(request, username)
            if not is_allowed:
                return APIV2FailJsonResponse(message, code=ApiErrorCodeEnumV2.ACCESS_PERMISSION_DENIED.value)

        # 获取用户数据
        ok, message, data = usermgr.get_user(username, "v2")
        if not ok:
            return APIV2FailJsonResponse(message, code=ApiErrorCodeEnumV2.USER_NOT_EXISTS2.value)

        return APIV2OKJsonResponse("get user information succeeded", data=data)


########
#  v3  #
########


class CheckLoginViewV3(View):
    def get(self, request):
        # 验证Token参数
        is_valid, username, message = validate_bk_token(request.GET)
        if not is_valid:
            return APIV3FailJsonResponse(message, code=ApiErrorCodeEnumV3.PARAM_NOT_VALID.value)
        return APIV3OKJsonResponse("user authentication succeeded", data={"bk_username": username})


class UserViewV3(View):
    def get(self, request):
        """
        获取用户信息API
        v3, 直接返回usermgr返回的内容不做字段转换
        """
        # 验证Token参数
        is_valid, username, message = validate_bk_token(request.GET)
        if not is_valid:
            # 如果是ESB的请求，可以直接从参数中获取用户id
            is_from_esb = is_request_from_esb(request)
            username = request.GET.get("bk_username")
            if not is_from_esb or not username:
                return APIV3FailJsonResponse(message, code=ApiErrorCodeEnumV3.PARAM_NOT_VALID.value)

        # 获取用户数据
        ok, message, data = usermgr.get_user(username, "v3")
        if not ok:
            return APIV3FailJsonResponse(message, code=ApiErrorCodeEnumV3.USER_NOT_EXISTS2.value)

        return APIV3OKJsonResponse("get user information succeeded", data=data)
