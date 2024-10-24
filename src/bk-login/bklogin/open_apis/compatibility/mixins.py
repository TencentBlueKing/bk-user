# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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

from typing import Dict

from django.conf import settings
from django.http import JsonResponse

from .constants import CompatibilityApiErrorCodeEnum, CompatibilityApiErrorCodeMap


class CompatibilityApiMixin:
    """兼容API Mixin"""

    api_version = "v1"

    @staticmethod
    def is_request_from_esb(request):
        """
        请求是否来自ESB
        """
        x_app_token = request.META.get("HTTP_X_APP_TOKEN")
        x_app_code = request.META.get("HTTP_X_APP_CODE")
        return bool(x_app_code == "esb" and x_app_token == settings.BK_PAAS_APP_SECRET)

    def fail_response(self, error_code: CompatibilityApiErrorCodeEnum, message: str) -> JsonResponse:
        code = CompatibilityApiErrorCodeMap[self.api_version][error_code]  # type: ignore
        if self.api_version == "v2":
            return JsonResponse({"result": False, "bk_error_code": code, "bk_error_msg": message, "data": {}})

        return JsonResponse({"result": False, "code": code, "message": message, "data": {}})

    def ok_response(self, data: Dict) -> JsonResponse:
        code = CompatibilityApiErrorCodeMap[self.api_version][CompatibilityApiErrorCodeEnum.SUCCESS]  # type: ignore
        if self.api_version == "v2":
            return JsonResponse({"result": True, "bk_error_code": code, "bk_error_msg": "", "data": data})

        return JsonResponse({"result": True, "code": code, "message": "", "data": data})

    @property
    def username_key(self) -> str:
        return "bk_username" if self.api_version in ["v2", "v3"] else "username"
