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
from django.db.models import ManyToOneRel
from rest_framework import filters


class MultipleFieldFilter(filters.SearchFilter):
    """多字段过滤器, 同时支持标准和非标准过滤"""

    def filter_queryset(self, request, queryset, view):
        """标准 filter"""

    def filter_by_params(self, params: dict, queryset):
        """非标准 filter"""
        available_fields = [
            getattr(f, "name") for f in queryset.model._meta.get_fields() if not isinstance(f, ManyToOneRel)
        ]
        query_params = {key: value for key, value in params.items() if key in available_fields}
        return queryset.filter(**query_params).only(*params.get("fields", []))
