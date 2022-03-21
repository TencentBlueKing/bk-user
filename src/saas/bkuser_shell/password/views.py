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
import logging

import bkuser_sdk
from bkuser_shell.apis.viewset import BkUserApiViewSet
from bkuser_shell.common.error_codes import error_codes
from bkuser_shell.common.response import Response

from bkuser_global.drf_crown import inject_serializer

from . import serializers

logger = logging.getLogger("root")


class PasswordViewSet(BkUserApiViewSet):

    permission_classes: list = []

    @inject_serializer(body_in=serializers.ResetPasswordEmailSerializer, tags=["password"])
    def reset(self, request, validated_data):
        """生成用户 token"""
        email = validated_data["email"]
        api_instance = bkuser_sdk.ProfilesApi(self.get_api_client_by_request(request))
        try:
            profile = api_instance.v2_profiles_read(lookup_value=email, lookup_field="email")
        except Exception:  # pylint: disable=broad-except
            """吞掉异常，保证不能判断出邮箱是否存在"""
            logger.exception("failed to get profile by email<%s>", email)
            return Response(data={})

        try:
            # 调用后台接口重置密码
            api_instance.v2_profiles_generate_token(lookup_value=profile.id, body={}, lookup_field="id")
        except Exception:  # pylint: disable=broad-except
            logger.exception("failed to generate token of profile<%s>. [profile.id=%s]", profile.username, profile.id)

        return Response(data={})

    @inject_serializer(body_in=serializers.ResetByTokenSerialzier, tags=["password"])
    def reset_by_token(self, request, validated_data):
        """通过 token 重置"""
        token = validated_data["token"]
        password = validated_data["password"]

        api_instance = bkuser_sdk.ProfilesApi(self.get_api_client_by_request(request))
        profile = api_instance.v2_retrieve_by_token(token=token)
        # 由于该接口无登录态，我们只能认为访问该链接的人即用户所有者
        request.user.username = profile.username

        profiles_api_instance = bkuser_sdk.ProfilesApi(self.get_api_client_by_request(request, user_from_token=True))
        body = {"password": password}

        # 调用后台接口重置密码
        profiles_api_instance.v2_profiles_partial_update(lookup_value=profile.id, body=body, lookup_field="id")

        return Response(data={})

    @inject_serializer(body_in=serializers.ModifyPassWordSerialzier, tags=["password"])
    def modify(self, request, validated_data):
        if not request.user or not request.user.is_authenticated:
            raise error_codes.USER_MISS_AUTH

        username = request.user.username
        api_instance = bkuser_sdk.ProfilesApi(self.get_api_client_by_request(request))
        profile = api_instance.v2_profiles_read(lookup_value=username)

        api_instance.v2_profiles_modify_password(
            lookup_value=profile.id,
            body=validated_data,
            lookup_field="id",
        )
        return Response(data={})
