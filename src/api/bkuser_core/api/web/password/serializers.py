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

from rest_framework import serializers

from bkuser_core.api.web.serializers import Base64OrPlainField
from bkuser_core.api.web.utils import get_raw_password, get_token_handler


class PasswordResetSendEmailInputSLZ(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=254)


class PasswordResetSendSMSInputSLZ(serializers.Serializer):
    telephone = serializers.CharField(required=True, max_length=32)


class PasswordResetSendSMSOutputSLZ(serializers.Serializer):
    verification_code_token = serializers.CharField(required=True, max_length=254)
    telephone = serializers.CharField(required=True, max_length=16)


class PasswordVerifyVerificationCodeInputSLZ(serializers.Serializer):
    verification_code_token = serializers.CharField(required=True, max_length=254)
    verification_code = serializers.CharField(required=True)


class PasswordVerifyVerificationCodeOutputSLZ(serializers.Serializer):
    token = serializers.CharField(required=True, max_length=254)


class PasswordResetByTokenInputSLZ(serializers.Serializer):
    token = serializers.CharField(required=True, max_length=254)
    password = Base64OrPlainField(required=True, max_length=254)

    def validate(self, attrs):
        token_holder = get_token_handler(token=attrs["token"])
        profile = token_holder.profile
        # 对于密码输入可能是明文也可能是密文，根据配置自动判断解析出明文（密文只是与前端加密传递，与后续逻辑无关）
        attrs["password"] = get_raw_password(profile.category_id, attrs["password"])
        return attrs


class PasswordModifyInputSLZ(serializers.Serializer):
    old_password = Base64OrPlainField(required=True, max_length=254)
    new_password = Base64OrPlainField(required=True, max_length=254)

    def validate(self, attrs):
        # 根据context，获取操作用户的目录id
        category_id = self.context["category_id"]
        # 解析密码是否加密
        attrs["old_password"] = get_raw_password(category_id, attrs["old_password"])
        attrs["new_password"] = get_raw_password(category_id, attrs["new_password"])
        return attrs


class PasswordListSettingsByTokenInputSLZ(serializers.Serializer):
    token = serializers.CharField(required=False, max_length=254)
