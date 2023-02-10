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
import base64
import datetime
from typing import List

from django.conf import settings
from django.utils.encoding import force_bytes, force_str
from rest_framework import fields, serializers

from .utils import expand_extra_fields, get_extras_with_default_values
from bkuser_core.profiles.models import Profile

# 公共的slz, 可能可以挪到别的地方, 后续再看


class DurationTotalSecondField(fields.Field):
    def to_internal_value(self, value) -> datetime.timedelta:
        if isinstance(value, float):
            value = str(value)
        return fields.parse_duration(value)

    def to_representation(self, value: datetime.timedelta):
        return value.total_seconds()


class StringArrayField(fields.CharField):
    """
    String representation of an array field.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.delimiter = kwargs.get("delimiter", ",")

    def to_internal_value(self, data) -> List[str]:
        # convert string to list
        data = super().to_internal_value(data)
        return [x for x in data.split(self.delimiter) if x]


def is_base64(value: str) -> bool:
    """判断字符串是否为 base64 编码"""
    try:
        return base64.b64encode(base64.b64decode(value)) == force_bytes(value)
    except Exception:  # pylint: disable=broad-except
        return False


class Base64OrPlainField(serializers.CharField):
    """兼容 base64 和纯文本字段"""

    def to_internal_value(self, data) -> str:
        if is_base64(data):
            return force_str(base64.b64decode(data))
        return super().to_internal_value(data)


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.

    support ?fields=id,username in GET
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        # fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        fields = self.context['request'].query_params.get('fields')
        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProfileDetailDepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    category_id = serializers.IntegerField(required=False)


class ProfileDetailLeaderSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    username = serializers.CharField()
    display_name = serializers.CharField(read_only=True)


# class ProfileDetailOutputSLZ(serializers.Serializer):
class ProfileDetailOutputSLZ(DynamicFieldsModelSerializer):
    # Q: 不需要返回所有字段吧
    # A: 需要, 目前前端的交互式, 列表点击直接拿数据渲染表单, 变更提交, 没有再次获取
    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "qq",
            "email",
            "telephone",
            "wx_userid",
            "domain",
            "display_name",
            "status",
            "staff_status",
            "position",
            "enabled",
            "password_valid_days",
            "account_expiration_date",
            "country_code",
            "iso_code",
            "time_zone",
            "last_login_time",
            "create_time",
            "update_time",
            "logo",
            "extras",
            "departments",
            "leader",
        )

    # id = serializers.CharField(required=False, help_text="用户ID")
    # username = serializers.CharField(required=False, help_text="用户名")
    # qq = serializers.CharField(required=False, help_text="QQ")
    # email = serializers.CharField(required=False, help_text="邮箱")
    # telephone = serializers.CharField(required=False, help_text="电话")
    # wx_userid = serializers.CharField(required=False, help_text="微信用户id")
    # domain = serializers.CharField(required=False, help_text="域")
    # display_name = serializers.CharField(required=False, help_text="中文名")
    # status = serializers.CharField(required=False, help_text="账户状态")
    # staff_status = serializers.CharField(required=False, help_text="在职状态")
    # position = serializers.CharField(required=False, help_text="职位")
    # enabled = serializers.BooleanField(required=False, help_text="是否启用", default=True)
    # # extras = serializers.JSONField(required=False, help_text="扩展字段")
    # password_valid_days = serializers.IntegerField(required=False, help_text="密码有效期")
    # account_expiration_date = serializers.CharField(required=False)
    # country_code = serializers.CharField(required=False, help_text="国家码")
    # iso_code = serializers.CharField(required=False, help_text="国家码")
    # time_zone = serializers.CharField(required=False, help_text="时区")

    # last_login_time = serializers.DateTimeField(required=False, help_text="最后登录时间")

    # create_time = serializers.DateTimeField(required=False, help_text="创建时间")
    # update_time = serializers.DateTimeField(required=False, help_text="更新时间")
    departments = ProfileDetailDepartmentSerializer(many=True, required=False, help_text="部门列表")

    # NOTE: 老的代码用的leader, 理论上应该换成leaders
    # leaders = ProfileDetailLeaderSerializer(many=True, required=False, help_text="上级列表", source="leader")
    leader = ProfileDetailLeaderSerializer(many=True, required=False, help_text="上级列表")

    logo = serializers.SerializerMethodField(required=False)
    extras = serializers.SerializerMethodField(required=False, read_only=True)

    def get_extras(self, obj: "Profile") -> dict:
        """尝试从 context 中获取默认字段值"""
        return get_extras_with_default_values(obj.extras)

    def get_logo(self, data):
        logo = data.logo
        if not logo:
            # logo转成 "data:image/png;base64,xxxxx"
            return settings.DEFAULT_LOGO_DATA

        return logo

    # NOTE: 部门下的用户列表需要把字段extras打平到profile的字段(用于页面展示+修改表单直接编辑/提交)
    def to_representation(self, instance):
        data = super().to_representation(instance)

        fields = self.context['request'].query_params.get('fields')
        if fields:
            fields = fields.split(',')
        return expand_extra_fields(data, fields=fields)
