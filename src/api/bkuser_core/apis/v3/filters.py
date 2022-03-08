"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging
from dataclasses import dataclass, field
from typing import ClassVar, Generator, List, Optional

from django.db.models import CharField, DateTimeField, FloatField, IntegerField, TextField
from rest_framework import filters, viewsets

from .exceptions import QueryTooLong

logger = logging.getLogger(__name__)


@dataclass
class FieldFilter:
    view_set: viewsets.ViewSet
    limit: ClassVar[Optional[int]] = None

    def extract_fields(self, queryset) -> Generator[str, None, None]:
        raise NotImplementedError

    def get_key(self, key: str) -> str:
        raise NotImplementedError

    def gen_query(self, queryset, params: dict) -> dict:

        query = {}
        for key, value in params.items():
            if key not in list(self.extract_fields(queryset)):
                continue

            if self.limit and len(value) > self.limit:
                raise QueryTooLong(f"当前过滤长度[{len(value)}]超过字段[{key}]限制[{self.limit}]")

            query[self.get_key(key)] = value

        return query


class ForeignFieldFilter(FieldFilter):
    limit = 100

    def extract_fields(self, queryset) -> Generator[str, None, None]:
        return (x for x in getattr(self.view_set, "foreign_fields", []))

    def get_key(self, key: str) -> str:
        return f"{key}__in"


class IContainFieldFilter(FieldFilter):
    limit = 100

    def extract_fields(self, queryset) -> Generator[str, None, None]:
        available_fields = queryset.model._meta.get_fields()
        for f in available_fields:
            if isinstance(f, (CharField, TextField, DateTimeField)):
                yield f.name

    def get_key(self, key) -> str:
        return f"{key}__icontains"


class PlainFieldFilter(FieldFilter):
    def extract_fields(self, queryset) -> Generator[str, None, None]:
        available_fields = queryset.model._meta.get_fields()
        for f in available_fields:
            if isinstance(f, (IntegerField, FloatField)):
                yield f.name

    def get_key(self, key) -> str:
        return key


class InFieldFilter(FieldFilter):
    limit = 1000

    def extract_fields(self, queryset) -> Generator[str, None, None]:
        return (x for x in getattr(self.view_set, "in_fields", []))

    def get_key(self, key: str) -> str:
        return key


@dataclass
class MultipleFieldFilter(filters.SearchFilter):
    """多字段过滤器, 同时支持标准和非标准过滤"""

    field_filters: List = field(
        default_factory=lambda: [ForeignFieldFilter, IContainFieldFilter, PlainFieldFilter, InFieldFilter]
    )

    def filter_by_params(self, queryset, params: dict, view):
        """根据不同字段类型进行多字段过滤"""

        query = {}
        for f_filter in self.field_filters:
            query.update(f_filter(view).gen_query(queryset, params))

        # in operator on many-to-many fields may cause duplicate results, so we use distinct
        logger.debug(f"trying to query via multiple fields: {query}")
        return queryset.filter(**query).distinct()
