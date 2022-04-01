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
import json
import logging
import math
from collections import OrderedDict
from typing import Callable, Optional

from bkuser_shell.common.core_client import get_api_client
from bkuser_shell.common.response import Response
from django.conf import settings
from django.utils.translation import get_language
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from bkuser_global.utils import force_str_2_bool

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 500

    def paginate_queryset(self, queryset, request, view=None):
        if force_str_2_bool(request.query_params.get("no_page", False)):
            return None

        return super(StandardResultsSetPagination, self).paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )


class BkUserApiViewSet(GenericViewSet):
    ACTION_ID = None

    permission_classes = [
        IsAuthenticated,
    ]

    @staticmethod
    def get_client_ip(request) -> Optional[str]:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            logger.debug("HTTP_X_FORWARDED_FOR exist, fetching from it")
            ip = x_forwarded_for.split(",")[0]
        else:
            for h in ["REMOTE_ADDR", "X-Real-IP"]:
                ip = request.META.get(h)
                if ip:
                    logger.debug("fetching client ip from %s", h)
                    break

        return ip

    def _prepare_headers(
        self, request, force_action_id: str = "", no_auth: bool = False, user_from_token: bool = False
    ):
        """构建通用 Headers"""
        headers = make_default_headers(request.user.username)
        ip = self.get_client_ip(request)
        if ip:
            headers.update({settings.CLIENT_IP_FROM_SAAS_HEADER: ip})

        action_id = force_action_id or self.ACTION_ID
        if not no_auth and action_id and settings.ENABLE_IAM:
            # 需要走 iam 主动标记
            headers.update(
                {
                    settings.API_NEED_IAM_HEADER_NAME: True,
                    settings.API_IAM_ACTION_ID_HEADER_NAME: action_id,
                    settings.API_FORCE_NO_CACHE_HEADER_NAME: True,
                }
            )
        if user_from_token:
            headers.update(
                {
                    "user_from_token": True,
                }
            )

        return headers

    def get_api_client_by_request(
        self, request, force_action_id: str = "", no_auth: bool = False, user_from_token: bool = False
    ):
        """从 request 中获取 api client"""
        return get_api_client(self._prepare_headers(request, force_action_id, no_auth, user_from_token))

    @staticmethod
    def get_paging_results(list_func: Callable, page_size: int = 50, **kwargs) -> list:
        """按照 id 排序分页拉取"""

        # 后端 API 服务中 id 都是自增的，所以按照 id 排序，新增内容只会往列表最后插入
        first_results = list_func(page_size=page_size, ordering="id", **kwargs)
        count = first_results["count"]
        paging_results: list = first_results["results"]

        if count <= page_size:
            return paging_results

        # 剩余的迭代拉取次数(减去第一次)
        post_times = int(math.ceil(count / page_size)) - 1
        modified_during_list = False
        for i in range(post_times):
            # 从第二页开始拉取
            r = list_func(page_size=page_size, ordering="id", page=i + 2, **kwargs)
            paging_results.extend(r["results"])

            if r["count"] != count:
                modified_during_list = True

        if modified_during_list:
            # 当前使用的 count/page 的分页方式并不能保证后端在循环分页请求期间数据有更新
            # 由于通过 SaaS 重新刷新的操作是廉价的，所以我们并不针对这样小概率的场景做额外的操作
            logger.warning("data changed during listing %s", list_func)

        return paging_results

    def get_api_path(self, request) -> str:
        """获取真实 API Path"""
        if settings.SITE_URL == "/":
            return request.path

        return "/" + request.path.replace(settings.SITE_URL, "")

    def call_through_api(self, request):
        client = self.get_api_client_by_request(request)

        urllib3_resp = client.call_api(
            resource_path=self.get_api_path(request),
            method=request.method,
            body=request.data,
            query_params=request.query_params,
            _return_http_data_only=True,
            _preload_content=False,
        )

        resp = Response(
            data=json.loads(urllib3_resp.data),
            status=urllib3_resp.status,
            content_type=urllib3_resp.headers.get("Content-Type"),
        )
        return resp


def make_default_headers(operator: str) -> dict:
    return {
        settings.API_OPERATOR_HEADER_NAME: operator,
        settings.API_FORCE_RAW_RESP_HEADER_NAME: True,
        settings.API_FORCE_RAW_USERNAME_HEADER_NAME: True,
        # SaaS 和 API 之间交互，走私有 token
        settings.API_AUTH_TOKEN_PAIR[0]: settings.API_AUTH_TOKEN_PAIR[1],
        "Accept-Language": get_language(),
    }
