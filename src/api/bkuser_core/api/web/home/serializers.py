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

from bkuser_core.categories.constants import CategoryStatus
from bkuser_core.categories.models import ProfileCategory


class CategoryOutputSLZ(serializers.ModelSerializer):
    # TODO: same as api/web/category/serializers.py:CategoryDetailOutputSLZ =>       remove it if not used
    configured = serializers.SerializerMethodField()
    # unfilled_namespaces = serializers.SerializerMethodField(required=False)
    activated = serializers.SerializerMethodField()

    syncing = serializers.BooleanField(read_only=True, required=False, allow_null=True)

    def get_configured(self, obj) -> bool:
        return obj.configured

    # def get_unfilled_namespaces(self, obj) -> List[str]:
    #     # NOTE: 每个category产生一次查询
    #     unfilled_nss = set(obj.get_unfilled_settings().values_list("namespace", flat=True))
    #     return list(unfilled_nss)

    def get_activated(self, obj) -> bool:
        # TODO: make this a model property?
        return obj.status == CategoryStatus.NORMAL.value

    class Meta:
        model = ProfileCategory
        fields = "__all__"
