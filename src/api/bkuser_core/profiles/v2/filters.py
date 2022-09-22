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
import logging
from itertools import chain

from django.db.models import QuerySet

from bkuser_core.apis.v2.viewset import AdvancedSearchFilter
from bkuser_core.categories.cache import get_default_category_domain_from_local_cache

logger = logging.getLogger(__name__)


class ProfileSearchFilter(AdvancedSearchFilter):
    """专供 profile 搜索使用"""

    def make_lookups(self, query_data: dict, queryset: QuerySet, search_field: str) -> QuerySet:
        """针对 username 字段做特殊处理"""

        if not search_field == "username":
            return super().make_lookups(query_data, queryset, search_field)

        # FIXME: 逐步去除参数/弱化, 直到删除这里的逻辑

        exact_lookups, fuzzy_lookups = query_data.get("exact_lookups"), query_data.get("fuzzy_lookups")
        # default_domain = ProfileCategory.objects.get_default().domain
        default_domain = get_default_category_domain_from_local_cache()
        condition_str = 'if(`domain`=%s, `username`, CONCAT(`username`, "@", `domain`))'
        # filter by time
        queryset = queryset.filter(self.make_time_filter(query_data))

        if exact_lookups:
            # 意图: 如果记录的domain == default.local则直接username=%s, 否则是 username@domain=%s
            lookup_sql = " OR ".join([f"({condition_str}=%s )"] * len(exact_lookups))
            lookups = exact_lookups
        elif fuzzy_lookups:
            lookup_sql = " OR ".join([f"{condition_str} LIKE %s"] * len(fuzzy_lookups))
            # https://docs.djangoproject.com/en/1.11/ref/models/querysets/#extra
            # 格外注意这里的参数拼接，任何用户输入都需要通过 Django 的方式放入语句
            lookups = [f"%{x}%" for x in fuzzy_lookups]
        else:
            return queryset

        # 最短匹配排在前面
        if fuzzy_lookups:
            queryset = self._try_best_match(query_data.get("best_match"), queryset, condition_str, [default_domain])

        # 相当于每一个查询都包含两个参数
        # if(`domain`=%s, `username`, CONCAT(`username`, "@", `domain`))=%s
        params = list(chain.from_iterable(zip([default_domain] * len(lookups), lookups)))
        return queryset.extra(where=[lookup_sql], params=params)
