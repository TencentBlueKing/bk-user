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
from base64 import b64encode
from collections import OrderedDict
from typing import TYPE_CHECKING
from urllib import parse

from rest_framework.pagination import CursorPagination

if TYPE_CHECKING:
    from django.db.models import QuerySet


class AdvancedPagination(CursorPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def encode_cursor(self, cursor):
        """
        Given a Cursor instance, return an url with encoded cursor.
        """
        tokens = {}
        if cursor.offset != 0:
            tokens["o"] = str(cursor.offset)
        if cursor.reverse:
            tokens["r"] = "1"
        if cursor.position is not None:
            tokens["p"] = cursor.position

        querystring = parse.urlencode(tokens, doseq=True)
        return b64encode(querystring.encode("ascii")).decode("ascii")

    def get_paginated_response(self, data: "QuerySet"):
        return OrderedDict(
            [
                ("count", len(data)),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )
