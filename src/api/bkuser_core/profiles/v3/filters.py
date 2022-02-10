"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.db.models import ManyToManyField, ManyToManyRel, ManyToOneRel
from rest_framework import filters


class MultipleFieldFilter(filters.SearchFilter):
    """多字段过滤器, 同时支持标准和非标准过滤"""

    def filter_by_params(self, params: dict, queryset, view):
        """非标准 filter"""
        plain_fields = [
            f.name
            for f in queryset.model._meta.get_fields()
            if not isinstance(f, (ManyToOneRel, ManyToManyRel, ManyToManyField))
        ]
        plain_query_params = {key: value for key, value in params.items() if key in plain_fields}
        m2m_query_params = {f"{key}__in": value for key, value in params.items() if key in view.supported_m2m_fields}
        # in operator on many-to-many fields may cause duplicate results, so we use distinct
        return queryset.filter(**m2m_query_params, **plain_query_params).distinct()
