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

from rest_framework.filters import BaseFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    # max_page_size = 1000
    page_query_param = "page"

    def get_paginated_response(self, data):
        return Response({"count": self.page.paginator.count, "results": data})


class StartTimeEndTimeFilterBackend(BaseFilterBackend):
    # NOTE: current only support create_time
    # if got update_time, we should modify this to support
    # use Q("{}__gte".format(field), start_time) & Q("{}__lte".format(field), end_time)
    def filter_queryset(self, request, queryset, view):
        start_time = request.query_params.get("start_time")
        if start_time:
            queryset = queryset.filter(create_time__gte=start_time)
        end_time = request.query_params.get("end_time")
        if end_time:
            queryset = queryset.filter(create_time__lte=end_time)

        return queryset


class LoginLogFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        is_success = request.query_params.get("is_success")
        logger.debug("login_in filter: is_success:<{}>".format(is_success))
        if is_success:
            queryset = queryset.filter(is_success=is_success)
        username = request.query_params.get("username")
        logger.debug("login_in filter: username:<{}>".format(username))
        if username:
            queryset = queryset.filter(profile__username=username)

        return queryset
