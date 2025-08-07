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

from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status
from rest_framework.response import Response

from bkuser.apps.audit.constants import OPENWEB_API_TYPE_MAPPING

logger = logging.getLogger("audit")


class OpenWebApiAuditMiddleware(MiddlewareMixin):
    """OpenWeb API 审计中间件"""

    def is_open_web_api(self, request):
        return request.path.startswith("/api/v3/open-web/") and request.method == "GET"

    def process_request(self, request):
        # 若接口不为 open-web 接口，则直接返回
        if not self.is_open_web_api(request):
            return

        # 解析 URL 路径
        request.resolved_path = resolve(request.path)

        # TODO：校验是否请求来自浏览器，若不为浏览器则拒接访问

    def process_response(self, request, response):
        # 若接口路径匹配错误，则会返回 TemplateResponse，此时不记录日志
        # 故需要判断 response 是否为 drf Response 类型
        if self.is_open_web_api(request) and isinstance(response, Response):
            self._create_audit_record_log(request, response)

        return response

    def _create_audit_record_log(self, request, response):
        """记录OpenWeb API审计日志"""
        # 直接将审计数据作为 logger 的 extra 参数
        extra_data = {
            "event_type": "open_web_api_access",
            "bk_username": request.user.username,
            "tenant_id": request.META.get("HTTP_X_BK_TENANT_ID", ""),
            "api_type": self._get_api_type(request),
            # 请求信息
            "request_path": request.path,
            "x_forwarded_for": request.META.get("HTTP_X_FORWARDED_FOR", ""),
            "x_real_ip": request.META.get("HTTP_X_REAL_IP", ""),
            "remote_addr": request.META.get("REMOTE_ADDR", ""),
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            "path_params": list(request.resolved_path.kwargs.values()),
            "query_params": request.GET.dict(),
            # 响应信息
            "status_code": response.status_code,
            "result_count": self._get_result_count(response),
            "object_ids": self._get_object_ids(response, request),
        }

        if status.is_success(response.status_code):
            logger.info(
                "[OpenWeb API] succeeded: bk_username: %s, tenant_id: %s, api_type: %s, status_code: %s",
                extra_data.get("bk_username"),
                extra_data.get("tenant_id"),
                extra_data.get("api_type"),
                extra_data.get("status_code"),
                extra=extra_data,
            )
        else:
            logger.error(
                "[OpenWeb API] failed: bk_username: %s, tenant_id: %s, api_type: %s, status_code: %s",
                extra_data.get("bk_username"),
                extra_data.get("tenant_id"),
                extra_data.get("api_type"),
                extra_data.get("status_code"),
                extra=extra_data,
            )

    def _get_api_type(self, request):
        # 获取 URL name 映射的 API 类型
        url_name = request.resolved_path.url_name
        return OPENWEB_API_TYPE_MAPPING.get(url_name)

    def _is_paginated_api(self, response):
        return (
            isinstance(response.data, dict)
            and "results" in response.data
            and "count" in response.data
            and isinstance(response.data["results"], list)
        )

    def _get_result_count(self, response):
        if not status.is_success(response.status_code):
            return 0

        # 请求成功时，提取结果数量
        # 若为 list 分页接口，则返回分页结果数量
        if self._is_paginated_api(response):
            return len(response.data["results"])

        # 若为 list 非分页接口，则直接返回结果数量
        if isinstance(response.data, list):
            return len(response.data)

        # 否则一定为 retrieve 接口，返回 1
        return 1

    def _get_object_ids(self, response, request):
        if not status.is_success(response.status_code):
            return []

        # 请求成功时，提取 ID 或用户名
        # 若为 list 分页接口
        if self._is_paginated_api(response):
            items = response.data["results"]
        # 若为 list 非分页接口
        elif isinstance(response.data, list):
            items = response.data
        # 否则一定为 retrieve 接口，从路径参数中获取
        else:
            return list(request.resolved_path.kwargs.values())

        # 提取用户 bk_username 或 部门 ID
        if not items:
            return []

        if "id" in items[0]:
            return [item["id"] for item in items]

        if "bk_username" in items[0]:
            return [item["bk_username"] for item in items]

        # 如果既没有 id 也没有 bk_username，返回空列表
        return []
