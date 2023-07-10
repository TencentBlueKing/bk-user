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
from typing import Dict

from django.conf import settings
from rest_framework import serializers

from bkuser_core.api.web.serializers import StringArrayField
from bkuser_core.api.web.utils import (
    escape_value,
    expand_extra_fields,
    get_default_category_id,
    get_extras_with_default_values,
    get_raw_password,
)
from bkuser_core.profiles.models import Profile
from bkuser_core.profiles.validators import validate_username


class LoginProfileRetrieveInputSLZ(serializers.Serializer):
    username = serializers.CharField(required=True)


class LoginProfileOutputSLZ(serializers.Serializer):
    username = serializers.SerializerMethodField(required=False)
    logo = serializers.SerializerMethodField(required=False)

    def get_username(self, obj):
        if get_default_category_id() == obj.category_id:
            return obj.username

        return f"{obj.username}@{obj.domain}"

    def get_logo(self, data):
        logo = data.logo
        if not logo:
            # logo转成 "data:image/png;base64,xxxxx"
            return settings.DEFAULT_LOGO_DATA

        return logo


class ProfileSearchInputSLZ(serializers.Serializer):
    # NOTE: 支持了departments, 但是去掉了leaders
    category_id = serializers.IntegerField()

    departments = StringArrayField(required=False, help_text="部门id列表")
    username = serializers.CharField(required=False, help_text="用户名")
    display_name = serializers.CharField(required=False, help_text="中文名")
    email = serializers.CharField(required=False, help_text="邮箱")
    telephone = serializers.CharField(required=False, help_text="电话")
    status = serializers.CharField(required=False, help_text="账户状态")
    staff_status = serializers.CharField(required=False, help_text="在职状态")

    # NOTE: 暂时不支持这四个字段
    # leaders
    # position
    # wx_userid
    # qq


class ProfileSearchResultLeaderSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    username = serializers.CharField()
    display_name = serializers.CharField(read_only=True)


class ProfileSearchResultDepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    category_id = serializers.IntegerField(required=False)


class ProfileSearchOutputSLZ(serializers.Serializer):
    # Q: 不需要返回所有字段吧
    # A: 需要, 搜索结果点击后直接渲染表单进行展示/更新
    id = serializers.CharField(required=False, help_text="用户ID")
    username = serializers.CharField(required=False, help_text="用户名")
    display_name = serializers.CharField(required=False, help_text="中文名")

    qq = serializers.CharField(required=False, help_text="QQ")
    email = serializers.CharField(required=False, help_text="邮箱")
    telephone = serializers.CharField(required=False, help_text="电话")
    wx_userid = serializers.CharField(required=False, help_text="微信用户id")
    domain = serializers.CharField(required=False, help_text="域")
    status = serializers.CharField(required=False, help_text="账户状态")
    staff_status = serializers.CharField(required=False, help_text="在职状态")
    position = serializers.CharField(required=False, help_text="职位")
    enabled = serializers.BooleanField(required=False, help_text="是否启用", default=True)
    password_valid_days = serializers.IntegerField(required=False, help_text="密码有效期")
    account_expiration_date = serializers.CharField(required=False)
    country_code = serializers.CharField(required=False, help_text="国家码")
    iso_code = serializers.CharField(required=False, help_text="国家码")
    time_zone = serializers.CharField(required=False, help_text="时区")

    last_login_time = serializers.DateTimeField(required=False, help_text="最后登录时间")

    create_time = serializers.DateTimeField(required=False, help_text="创建时间")
    update_time = serializers.DateTimeField(required=False, help_text="更新时间")
    departments = ProfileSearchResultDepartmentSerializer(many=True, required=False, help_text="部门列表")
    leaders = ProfileSearchResultLeaderSerializer(many=True, required=False, help_text="上级列表", source="leader")

    # extras = serializers.JSONField(required=False, help_text="扩展字段")
    extras = serializers.SerializerMethodField(required=False, read_only=True)

    def get_extras(self, obj: "Profile") -> Dict:
        """尝试从 context 中获取默认字段值"""
        return get_extras_with_default_values(obj.extras)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return expand_extra_fields(data)


class ProfileUpdateInputSLZ(serializers.ModelSerializer):
    leader = serializers.ListField(child=serializers.IntegerField(), required=False)
    departments = serializers.ListField(child=serializers.IntegerField(), required=False)
    password = serializers.CharField(required=False, write_only=True)
    display_name = serializers.CharField(required=False)
    old_password = serializers.CharField(required=False, write_only=True)  # 只有admin用户重置密码时才需要传递该字段

    class Meta:
        model = Profile
        # NOTE: 相对原来的api区别, 不支持extras/create_time/update_time更新
        exclude = ["category_id", "username", "domain", "extras", "create_time", "update_time"]

    def validate_password(self, password):
        return get_raw_password(self.instance.category_id, password)

    def validate_display_name(self, display_name):
        return escape_value(display_name)

    def validate_old_password(self, old_password):
        return get_raw_password(self.instance.category_id, old_password)


class ProfileCreateInputSLZ(serializers.ModelSerializer):
    category_id = serializers.IntegerField(required=False)

    # required
    username = serializers.CharField(validators=[validate_username])
    display_name = serializers.CharField()
    email = serializers.CharField()
    telephone = serializers.CharField()
    status = serializers.CharField()
    staff_status = serializers.CharField()

    # not required
    logo = serializers.CharField(required=False)
    position = serializers.IntegerField(required=False, allow_null=True)
    wx_userid = serializers.CharField(required=False, allow_blank=True, allow_null=True, default="")
    qq = serializers.CharField(required=False, allow_blank=True, allow_null=True, default="")
    account_expiration_date = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # not in the form, but in request body
    iso_code = serializers.CharField(required=False, default="CN")

    leader = serializers.ListField(required=False, child=serializers.IntegerField(), default=[])
    # required
    departments = serializers.ListField(child=serializers.IntegerField(), default=[])
    password_valid_days = serializers.IntegerField()

    # NOTE: 区别
    # extras = serializers.JSONField(required=False)
    # domain = serializers.CharField(validators=[validate_domain], required=False)
    # NOTE: 其他字段, 自行放入extras

    class Meta:
        model = Profile
        fields = (
            "category_id",
            "username",
            "display_name",
            "email",
            "telephone",
            "status",
            "staff_status",
            "logo",
            "position",
            "wx_userid",
            "qq",
            "account_expiration_date",
            "iso_code",
            "leader",
            "departments",
            "password_valid_days",
        )
        # exclude = ["password"]
        validators: list = []

    def validate_display_name(self, display_name):
        return escape_value(display_name)


class ProfileBatchDeleteInputSLZ(serializers.Serializer):
    id = serializers.IntegerField()


class ProfileBatchUpdateInputSLZ(serializers.ModelSerializer):
    # 批量更新时使用
    id = serializers.IntegerField(required=False)
    departments = serializers.ListField(required=False)
    # extras = serializers.JSONField(required=False)

    class Meta:
        model = Profile
        # NOTE: 差异点, 禁止更新password
        exclude = ["category_id", "username", "domain", "password"]
