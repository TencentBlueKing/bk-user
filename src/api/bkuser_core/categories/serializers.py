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

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import ValidationError

from bkuser_core.apis.v2.serializers import CustomFieldsModelSerializer
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.profiles.validators import validate_domain


class CategorySerializer(CustomFieldsModelSerializer):
    """用户目录 Serializer"""

    # NOTE: saas API 独立了, 对外 API 不需要这三个字段
    # configured = SerializerMethodField()
    # syncing = BooleanField(read_only=True, required=False, allow_null=True)
    # unfilled_namespaces = SerializerMethodField(required=False)

    # def get_configured(self, obj) -> bool:
    #     return obj.configured

    # def get_unfilled_namespaces(self, obj) -> List[str]:
    #     unfilled_nss = set(obj.get_unfilled_settings().values_list("namespace", flat=True))
    #     return list(unfilled_nss)

    class Meta:
        model = ProfileCategory
        fields = "__all__"


class CreateCategorySerializer(CategorySerializer):
    """用户目录 Serializer"""

    display_name = serializers.CharField()
    domain = serializers.CharField(validators=[validate_domain])

    def validate(self, data):
        if ProfileCategory.objects.filter(domain=data["domain"]).exists():
            raise ValidationError(_("登陆域为 {} 的用户目录已存在").format(data["domain"]))

        return super().validate(data)
