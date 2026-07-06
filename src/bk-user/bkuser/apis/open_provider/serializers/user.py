# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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
from django.conf import settings
from rest_framework import serializers

from bkuser.apis.open_provider.constants import PROVIDER_BATCH_SIZE


class UserCreateItemSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户唯一标识（数据源内）", max_length=128)
    username = serializers.CharField(help_text="用户名", max_length=128)
    full_name = serializers.CharField(help_text="姓名", max_length=128)
    email = serializers.EmailField(help_text="邮箱", required=False, default="")
    phone = serializers.CharField(help_text="手机号", required=False, default="", max_length=32)
    phone_country_code = serializers.CharField(
        help_text="手机国际区号",
        required=False,
        default=settings.DEFAULT_PHONE_COUNTRY_CODE,
        max_length=16,
    )
    extras = serializers.JSONField(help_text="自定义字段", required=False, default=dict)


class UserBatchCreateInputSLZ(serializers.Serializer):
    users = serializers.ListField(
        help_text="用户列表",
        child=UserCreateItemSLZ(),
        min_length=1,
        max_length=PROVIDER_BATCH_SIZE,
    )


class UserUpdateItemSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户唯一标识（数据源内）")
    username = serializers.CharField(help_text="用户名", required=False, max_length=128)
    full_name = serializers.CharField(help_text="姓名", required=False, max_length=128)
    email = serializers.EmailField(help_text="邮箱", required=False)
    phone = serializers.CharField(help_text="手机号", required=False, max_length=32)
    phone_country_code = serializers.CharField(help_text="手机国际区号", required=False, max_length=16)
    extras = serializers.JSONField(help_text="自定义字段", required=False)


class UserBatchUpdateInputSLZ(serializers.Serializer):
    users = serializers.ListField(
        help_text="用户列表",
        child=UserUpdateItemSLZ(),
        min_length=1,
        max_length=PROVIDER_BATCH_SIZE,
    )


class UserBatchDeleteInputSLZ(serializers.Serializer):
    ids = serializers.ListField(
        help_text="用户唯一标识列表",
        child=serializers.CharField(),
        min_length=1,
        max_length=PROVIDER_BATCH_SIZE,
    )
