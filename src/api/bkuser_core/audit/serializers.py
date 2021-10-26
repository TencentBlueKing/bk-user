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
from bkuser_core.common.serializers import CustomFieldsMixin
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class GeneralLogSerializer(CustomFieldsMixin, serializers.Serializer):
    id = serializers.IntegerField(help_text=_("ID"))
    extra_value = serializers.JSONField(help_text=_("额外信息"))
    operator = serializers.CharField(help_text=_("操作者"))
    create_time = serializers.DateTimeField(help_text=_("创建时间"))


class LoginLogSerializer(CustomFieldsMixin, serializers.Serializer):
    id = serializers.IntegerField(help_text=_("ID"))
    extra_value = serializers.JSONField(help_text=_("额外信息"))
    operator = serializers.CharField(help_text=_("操作者"))
    is_success = serializers.BooleanField(help_text=_("是否成功"))
    reason = serializers.CharField(help_text=_("失败原因"))
    create_time = serializers.DateTimeField(help_text=_("创建时间"))
    username = serializers.CharField(help_text=_("登录用户"), source="profile.username")
    profile_id = serializers.CharField(help_text=_("登录用户ID"), source="profile.id")
    category_id = serializers.CharField(help_text=_("登录用户"), source="profile.category_id")


class ResetPasswordLogSerializer(CustomFieldsMixin, serializers.Serializer):
    id = serializers.IntegerField(help_text=_("ID"))
    extra_value = serializers.JSONField(help_text=_("额外信息"))
    operator = serializers.CharField(help_text=_("操作者"))
    create_time = serializers.DateTimeField(help_text=_("创建时间"))
    username = serializers.CharField(help_text=_("登录用户"), source="profile.username")
    category_id = serializers.CharField(help_text=_("登录用户"), source="profile.category_id")
