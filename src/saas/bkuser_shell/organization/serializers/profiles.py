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
from rest_framework.serializers import (
    CharField,
    DateField,
    DateTimeField,
    IntegerField,
    JSONField,
    ListField,
    Serializer,
    SerializerMethodField,
)

from .departments import SubDepartmentSerializer
from bkuser_shell.organization.utils import expand_extra_fields, get_default_logo_url


class LeaderSerializer(Serializer):
    display_name = CharField()
    id = IntegerField()
    username = CharField()


class ProfileSerializer(Serializer):
    """用户序列化"""

    id = IntegerField(required=False)
    telephone = CharField(required=False)
    wx_userid = CharField(required=False)
    qq = CharField(required=False)
    password_valid_days = IntegerField(required=False)
    password = CharField(required=False)
    position = IntegerField(required=False)
    role = IntegerField(required=False)
    email = CharField(required=False)
    username = CharField(required=True)
    display_name = CharField(required=True)
    leader = ListField(required=False, default=[], child=LeaderSerializer())
    status = CharField(required=False)
    staff_status = CharField(required=False)
    iso_code = SerializerMethodField()
    extras = JSONField(required=False)
    logo = SerializerMethodField(required=False)
    category_id = IntegerField(required=False)
    departments = SubDepartmentSerializer(many=True)
    update_time = DateTimeField(required=False)
    create_time = DateTimeField(required=False)
    last_login_time = DateTimeField(required=False)
    account_expiration_date = CharField()

    def get_logo(self, data):
        if isinstance(data, dict):
            logo = data.get("logo")
        else:
            logo = data.logo

        if not self.context.get("request"):
            return logo

        if not logo:
            return get_default_logo_url(self.context.get("request"))

        return logo

    def get_iso_code(self, data):
        if isinstance(data, dict):
            return data["iso_code"].lower() or "cn"
        return data.iso_code

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not self.context.get("fields"):
            return data

        return expand_extra_fields(self.context.get("fields"), data)


class UpdateProfileSerializer(Serializer):
    id = IntegerField(required=False)
    telephone = CharField(required=False)
    wx_userid = CharField(required=False, allow_null=True, allow_blank=True)
    qq = CharField(required=False, allow_blank=True, allow_null=True)
    password_valid_days = IntegerField(required=False)
    password = CharField(required=False)
    email = CharField(required=False)
    display_name = CharField(required=False)
    leader = ListField(required=False)
    username = CharField(required=False)
    staff_status = CharField(required=False)
    status = CharField(required=False)
    position = IntegerField(required=False)
    iso_code = CharField(required=False)
    logo = CharField(required=False)
    departments = ListField(child=IntegerField(), required=False)
    account_expiration_date = CharField(required=False)


class ProfileExportSerializer(Serializer):
    display_name = CharField()
    username = CharField()
    leader = LeaderSerializer(many=True)
    department_name = SubDepartmentSerializer(many=True, source="departments")
    staff_status = CharField(required=False)
    status = CharField(required=False)
    extras = JSONField(default={})
    telephone = CharField()
    email = CharField()
    qq = CharField(required=False)
    position = IntegerField(required=False)
    wx_userid = CharField()
    iso_code = CharField()
    country_code = CharField()
    last_login_time = CharField()
    create_time = DateTimeField()
    account_expiration_date = DateField()

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["leader"] = ",".join(x["username"] for x in data["leader"])
        data["department_name"] = ",".join([x["full_name"] for x in data["department_name"]])
        return data
