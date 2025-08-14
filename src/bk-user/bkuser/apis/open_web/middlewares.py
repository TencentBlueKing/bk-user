# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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

import logging

from django.utils.deprecation import MiddlewareMixin
from rest_framework import status
from rest_framework.response import Response

from bkuser.apis.open_web.constants import OpenWebApiEnum

logger = logging.getLogger("open_web_api_access")

OPEN_WEB_API_TYPE_MAPPING = {
    "open_web.tenant_user.display_info.retrieve": OpenWebApiEnum.RETRIEVE_USER_DISPLAY_INFO,
    "open_web.tenant_user.display_info.list": OpenWebApiEnum.BATCH_QUERY_USER_DISPLAY_INFO,
    "open_web.tenant_user.search": OpenWebApiEnum.SEARCH_USER,
    "open_web.tenant_user.lookup": OpenWebApiEnum.BATCH_LOOKUP_USER,
    "open_web.tenant_department.search": OpenWebApiEnum.SEARCH_DEPARTMENT,
    "open_web.tenant_department.lookup": OpenWebApiEnum.BATCH_LOOKUP_DEPARTMENT,
    "open_web.tenant.virtual_user.list": OpenWebApiEnum.LIST_VIRTUAL_USER,
    "open_web.tenant_department.child.list": OpenWebApiEnum.LIST_DEPARTMENT_CHILD,
    "open_web.tenant_department.user.list": OpenWebApiEnum.LIST_DEPARTMENT_USER,
}


class OpenWebApiAuditMiddleware(MiddlewareMixin):
    """OpenWeb API 审计中间件"""

    def __init__(self, get_response):
        self.get_response = get_response

    def is_open_web_api(self, request):
        return request.path.startswith("/api/v3/open-web/") and request.method == "GET"

    def __call__(self, request):
        response = self.get_response(request)

        # 若接口路径匹配错误，则会返回 TemplateResponse，此时不记录日志
        # 故需要判断 response 是否为 drf Response 类型
        if self.is_open_web_api(request) and isinstance(response, Response):
            self.api_type = self._get_api_type(request)
            self._create_log(request, response)

        return response

    def _create_log(self, request, response):
        """记录OpenWeb API审计日志"""
        # 直接将审计数据作为 logger 的 extra 参数
        extra = {
            "bk_username": request.user.username,
            "tenant_id": request.META.get("HTTP_X_BK_TENANT_ID", ""),
            "api_type": self.api_type,
            # 请求信息
            "request_path": request.path,
            "x_forwarded_for": request.META.get("HTTP_X_FORWARDED_FOR", ""),
            "x_real_ip": request.META.get("HTTP_X_REAL_IP", ""),
            "remote_addr": request.META.get("REMOTE_ADDR", ""),
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            "path_params": list(request.resolver_match.kwargs.values()),
            "query_params": request.GET.dict(),
            # 响应信息
            "status_code": response.status_code,
            "result_count": self._get_result_count(response),
            "object_ids": self._get_object_ids(request, response),
        }

        logger.info("", extra=extra)

    def _get_api_type(self, request):
        # 获取 URL name 映射的 API 类型
        url_name = request.resolver_match.url_name
        return OPEN_WEB_API_TYPE_MAPPING.get(url_name)

    def _get_result_count(self, response):
        if not status.is_success(response.status_code):
            return 0

        # 请求成功时，提取结果数量
        # 若为 list 分页接口，则返回分页结果数量
        if self.api_type == OpenWebApiEnum.LIST_VIRTUAL_USER:
            return len(response.data["results"])

        # 查询用户展示信息接口为 retrieve 接口，返回 1
        if self.api_type == OpenWebApiEnum.RETRIEVE_USER_DISPLAY_INFO:
            return 1

        # 否则一定为 list 非分页接口，则直接返回结果数量
        return len(response.data)

    def _get_object_ids(self, request, response):
        if not status.is_success(response.status_code):
            return []

        if self.api_type == OpenWebApiEnum.LIST_VIRTUAL_USER:
            return [item["bk_username"] for item in response.data["results"]]

        if self.api_type == OpenWebApiEnum.RETRIEVE_USER_DISPLAY_INFO:
            return list(request.resolver_match.kwargs.values())

        if self.api_type in [
            OpenWebApiEnum.SEARCH_DEPARTMENT,
            OpenWebApiEnum.BATCH_LOOKUP_DEPARTMENT,
            OpenWebApiEnum.LIST_DEPARTMENT_CHILD,
        ]:
            return [item["id"] for item in response.data]

        return [item["bk_username"] for item in response.data]
