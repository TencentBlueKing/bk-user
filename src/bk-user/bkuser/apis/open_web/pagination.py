# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from rest_framework.response import Response

from bkuser.common.pagination import CustomPageNumberPagination


class NoCountCustomPageNumberPagination(CustomPageNumberPagination):
    """
    基于 CustomPageNumberPagination 实现的轻量分页器,用于不需要 count 的场景
    """

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        page = self.get_page_number(request)
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        offset = (page - 1) * page_size
        return list(queryset[offset : offset + page_size])

    def get_paginated_response(self, data):
        return Response(data)

    def get_paginated_response_schema(self, schema):
        return schema


def gen_no_count_pagination_class(max_page_size: int):
    """根据最大页数生成 NoCountCustomPageNumberPagination"""

    return type("NoCountPagination", (NoCountCustomPageNumberPagination,), {"max_page_size": max_page_size})
