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
from django.conf import settings
from django.views.generic import View

from bklogin.common.error_codes import error_codes
from bklogin.common.response import APISuccessResponse
from bklogin.component.bk_user import api as bk_user_api

from .manager import BkTokenManager


class CheckTokenApi(View):
    def get(self, request, *args, **kwargs):
        bk_token = request.GET.get(settings.BK_TOKEN_COOKIE_NAME)

        ok, username, msg = BkTokenManager().is_bk_token_valid(bk_token)
        if not ok:
            raise error_codes.VALIDATION_ERROR.f(msg)

        return APISuccessResponse({"bk_username": username})


class GetUserApi(View):
    def get(self, request, *args, **kwargs):
        bk_token = request.GET.get(settings.BK_TOKEN_COOKIE_NAME)

        ok, username, msg = BkTokenManager().is_bk_token_valid(bk_token)
        if not ok:
            raise error_codes.VALIDATION_ERROR.f(msg)

        user = bk_user_api.get_tenant_user(username)

        return APISuccessResponse(
            {
                "bk_username": user.id,
                "tenant_id": user.tenant_id,
                "full_name": user.full_name,
                "source_username": user.username,
                "language": user.language,
                "time_zone": user.time_zone,
            }
        )
