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
from typing import List

from bkuser_core.bkiam.serializers import AuthInfoSLZ
from bkuser_core.common.serializers import CustomFieldsModelSerializer
from bkuser_core.profiles.validators import validate_domain
from django.utils.translation import ugettext_lazy as _
from rest_framework.serializers import (
    BooleanField,
    CharField,
    FileField,
    IntegerField,
    ListField,
    Serializer,
    SerializerMethodField,
)
from rest_framework.validators import ValidationError

from .models import ProfileCategory


class ExtraInfoSLZ(Serializer):
    auth_infos = ListField(read_only=True, child=AuthInfoSLZ())
    callback_url = CharField(read_only=True)


class CategoryMetaSLZ(Serializer):
    """用户目录基本信息"""

    type = CharField(read_only=True)
    description = CharField(read_only=True)
    name = CharField(read_only=True)
    authorized = BooleanField(read_only=True, default=True)
    extra_info = ExtraInfoSLZ(read_only=True, default={})


class CategorySerializer(CustomFieldsModelSerializer):
    """用户目录 Serializer"""

    configured = SerializerMethodField()
    unfilled_namespaces = SerializerMethodField(required=False)

    def get_configured(self, obj) -> bool:
        return obj.configured

    def get_unfilled_namespaces(self, obj) -> List[str]:
        unfilled_nss = set(obj.get_unfilled_settings().values_list("namespace", flat=True))
        return list(unfilled_nss)

    class Meta:
        model = ProfileCategory
        fields = "__all__"


class CreateCategorySerializer(CategorySerializer):
    """用户目录 Serializer"""

    display_name = CharField()
    domain = CharField(validators=[validate_domain])

    def validate(self, data):
        if ProfileCategory.objects.filter(domain=data["domain"]).exists():
            raise ValidationError(_("登陆域为 {} 的用户目录已存在").format(data["domain"]))

        return super().validate(data)


class CategorySyncSerializer(Serializer):
    raw_data_file = FileField()


class CategoryTestConnectionSerializer(Serializer):
    connection_url = CharField()
    user = CharField(required=False)
    password = CharField(required=False)
    timeout_setting = IntegerField(required=False, default=120)
    use_ssl = BooleanField(default=False, required=False)


class CategoryTestFetchDataSerializer(Serializer):
    basic_pull_node = CharField()
    user_filter = CharField()
    organization_class = CharField()
    user_group_filter = CharField()
