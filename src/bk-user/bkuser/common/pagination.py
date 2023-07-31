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
from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .error_codes import error_codes


class CustomPageNumberPagination(PageNumberPagination):
    """
    该分页器继承PageNumberPagination后只对用于API返回的数据里去除previous和next参数
    """

    page_size_query_param = "page_size"

    def _positive_int(self, integer_string, strict=False, cutoff=None):
        """
        Cast a string to a strictly positive integer.
        copied from https://github.com/encode/django-rest-framework/blob/master/rest_framework/pagination.py#L22
        """
        try:
            ret = int(integer_string)
        except ValueError:
            raise error_codes.VALIDATION_ERROR.f("wrong page {}".format(integer_string))

        if ret < 0 or (ret == 0 and strict):
            raise error_codes.VALIDATION_ERROR.f("wrong page {}".format(ret))
        if cutoff:
            return min(ret, cutoff)
        return ret

    def get_page_number(self, request, paginator=None):
        """重载：去除支持page_number='last'等用于模板渲染的表达，仅仅支持数字"""
        page_number = request.query_params.get(self.page_query_param, 1)
        return self._positive_int(page_number, strict=True)

    def get_paginated_response(self, data):
        return Response(OrderedDict([("count", self.page.paginator.count), ("results", data)]))

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "example": 123,
                },
                "results": schema,
            },
        }
