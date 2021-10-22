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
from bkuser_shell.organization.utils import get_default_logo_url
from rest_framework.serializers import CharField, IntegerField, JSONField, ListField, Serializer, SerializerMethodField

from .departments import SubDepartmentSerializer


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
    departments = SubDepartmentSerializer(many=True)

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


class ProfileResultSerializer(Serializer):
    count = IntegerField()
    data = ProfileSerializer(many=True, source="results")


class LoginInfoSerializer(Serializer):
    username = CharField()
    logo = SerializerMethodField(required=False)

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


class ListProfilesSerializer(Serializer):
    keyword = CharField(required=False)
    page = IntegerField(required=False, default=1)
    page_size = IntegerField(required=False, default=10)


class CreateProfileSerializer(Serializer):
    category_id = IntegerField()
    telephone = CharField()
    wx_userid = CharField(required=False, allow_blank=True, allow_null=True, default="")
    qq = CharField(required=False, allow_blank=True, allow_null=True, default="")
    password_valid_days = IntegerField(required=False)
    email = CharField()
    username = CharField()
    display_name = CharField()
    leader = ListField(required=False, default=[])
    staff_status = CharField(required=False)
    status = CharField(required=False)
    position = IntegerField(required=False)
    iso_code = CharField(required=False, default="CN")
    logo = CharField(required=False)
    departments = ListField(child=IntegerField(), required=False, default=[])


class UpdateProfileSerializer(Serializer):
    id = IntegerField(required=False)
    telephone = CharField(required=False)
    wx_userid = CharField(required=False, allow_null=True, default="", allow_blank=True)
    qq = CharField(required=False, allow_blank=True, allow_null=True, default="")
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

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["leader"] = ",".join(x["username"] for x in data["leader"])
        data["department_name"] = ",".join([x["full_name"] for x in data["department_name"]])
        return data
