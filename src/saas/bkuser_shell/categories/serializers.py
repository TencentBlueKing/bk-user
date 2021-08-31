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
from bkuser_shell.bkiam.serializers import AuthInfoSLZ
from bkuser_shell.categories.constants import CategoryStatus
from django.utils.translation import ugettext_lazy as _
from rest_framework.serializers import (
    BooleanField,
    CharField,
    ChoiceField,
    DateTimeField,
    FileField,
    IntegerField,
    JSONField,
    ListField,
    Serializer,
    SerializerMethodField,
)


class ExtraInfoSLZ(Serializer):
    auth_infos = ListField(read_only=True, child=AuthInfoSLZ())
    callback_url = CharField(read_only=True)


class CategoryMetaSLZ(Serializer):
    """用户目录基本信息"""

    type = CharField(read_only=True)
    description = CharField(read_only=True)
    name = CharField(read_only=True)
    authorized = BooleanField(read_only=True)
    extra_info = ExtraInfoSLZ(read_only=True)


class DetailCategorySerializer(Serializer):
    id = IntegerField(required=False)
    domain = CharField()
    display_name = CharField()
    default = BooleanField()
    enabled = BooleanField()
    type = CharField()
    description = CharField()
    create_time = DateTimeField()
    update_time = DateTimeField()
    last_synced_time = DateTimeField()
    unfilled_namespaces = JSONField()
    configured = BooleanField(help_text="是否配置就绪")
    syncing = BooleanField(help_text="是否正在同步")
    activated = SerializerMethodField()

    def get_activated(self, obj) -> bool:
        if isinstance(obj, dict):
            return obj["status"] == CategoryStatus.NORMAL.value
        else:
            return getattr(obj, "status") == CategoryStatus.NORMAL.value


class CreateCategorySerializer(Serializer):
    domain = CharField(max_length=64, label=_("登陆域"))
    display_name = CharField(max_length=64, label=_("目录名"))
    activated = BooleanField(default=True)
    type = ChoiceField(default="local", choices=["mad", "ldap", "local"])


class UpdateCategorySerializer(Serializer):
    display_name = CharField(max_length=64, required=False)
    activated = BooleanField(default=True, required=False)
    description = CharField(required=False)


class ListCategorySerializer(Serializer):
    only_enable = BooleanField(default=False)


class CategorySyncSerializer(Serializer):
    file = FileField(required=False)


class CategoryTestConnectionSerializer(Serializer):
    connection_url = CharField(required=False)
    user = CharField(required=False)
    password = CharField(required=False)
    timeout_setting = IntegerField(required=False, default=120)
    use_ssl = BooleanField(default=False, required=False)


class CategoryTestFetchDataSerializer(Serializer):
    basic_pull_node = CharField(required=False)
    user_filter = CharField(required=False)
    organization_class = CharField(required=False)
    user_group_filter = CharField(required=False)


class CategoryExportSerializer(Serializer):
    department_ids = CharField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["department_ids"] = data["department_ids"].split(",")
        return data
