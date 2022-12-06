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


class PasswordResetByTokenInputSLZ(serializers.Serializer):
    token = serializers.CharField(required=True, max_length=254)
    password = Base64OrPlainField(required=True, max_length=254)

    def validate(self, attrs):
        new_attrs = attrs
        token = new_attrs["token"]
        password = new_attrs["password"]

        token_holder = get_token_handler(token)
        profile = token_holder.profile

        raw_password = get_raw_password(profile.category_id, password)
        new_attrs["password"] = raw_password

        return new_attrs


class PasswordModifyInputSLZ(serializers.Serializer):
    old_password = Base64OrPlainField(required=True, max_length=254)
    new_password = Base64OrPlainField(required=True, max_length=254)


class PasswordListSettingsByTokenInputSLZ(serializers.Serializer):
    token = serializers.CharField(required=True, max_length=254)
