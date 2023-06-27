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

from bkuser_core.profiles.constants import TIME_ZONE_CHOICES, LanguageEnum, RoleCodeEnum
from bkuser_core.profiles.models import Profile
from bkuser_core.profiles.utils import get_username
from bkuser_core.profiles.validators import validate_domain


class ProfileLoginSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="用户名")
    password = serializers.CharField(help_text="用户密码")
    domain = serializers.CharField(required=False, help_text="用户所属目录 domain，当登录用户不属于默认目录时必填")


class LoginUpsertSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, min_length=1, max_length=255)
    display_name = serializers.CharField(required=False, min_length=1, max_length=255, allow_blank=True)
    domain = serializers.CharField(required=False, validators=[validate_domain])

    qq = serializers.CharField(required=False, min_length=5, max_length=64, allow_blank=True)
    telephone = serializers.CharField(required=False, min_length=11, max_length=11)
    email = serializers.EmailField(required=False)
    role = serializers.ChoiceField(required=False, choices=RoleCodeEnum.get_choices())
    position = serializers.CharField(required=False)
    language = serializers.ChoiceField(required=False, choices=LanguageEnum.get_choices())
    time_zone = serializers.ChoiceField(required=False, choices=TIME_ZONE_CHOICES)
    status = serializers.CharField(required=False)
    staff_status = serializers.CharField(required=False)
    wx_userid = serializers.CharField(required=False, allow_blank=True)

    iso_code = serializers.CharField(required=False)


class LoginBatchQuerySerializer(serializers.Serializer):
    username_list = serializers.ListField(child=serializers.CharField(), required=False)
    is_complete = serializers.BooleanField(required=False)


class LoginBatchResponseSerializer(serializers.Serializer):
    username = serializers.SerializerMethodField()
    chname = serializers.CharField(source="display_name")
    display_name = serializers.CharField()
    qq = serializers.CharField()
    phone = serializers.CharField(source="telephone")
    wx_userid = serializers.CharField()
    language = serializers.CharField()
    time_zone = serializers.CharField()
    email = serializers.CharField()
    role = serializers.IntegerField()
    iso_code = serializers.CharField()

    def get_username(self, data):
        return get_username(
            data.category_id,
            data.username,
            data.domain,
        )


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    def get_username(self, data):
        return get_username(
            data.category_id,
            data.username,
            data.domain,
        )

    class Meta:
        model = Profile
        fields = [
            "username",
            "display_name",
            "email",
            "role",
            "status",
            "time_zone",
            "language",
            "domain",
            "category_id",
            "iso_code",
            # NOTE: 这里缩减登陆成功之后的展示字段
            # "position",
            # "logo_url", => to logo?
            # "telephone",
            # "wx_id",
            # "extras",
        ]
