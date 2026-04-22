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

import logging

from django.conf import settings
from rest_framework import status

from bkuser.apis.open_web.constants import OpenWebApiEnum
from bkuser.apps.tenant.constants import BuiltInTenantIDEnum

logger = logging.getLogger("open_web_api_access")

OPEN_WEB_API_MAP = {
    "open_web.tenant_user.search": OpenWebApiEnum.SEARCH_USER,
    "open_web.tenant_user.lookup": OpenWebApiEnum.BATCH_LOOKUP_USER,
    "open_web.tenant_department.search": OpenWebApiEnum.SEARCH_DEPARTMENT,
    "open_web.tenant.virtual_user.list": OpenWebApiEnum.LIST_VIRTUAL_USER,
    "open_web.tenant_department.child.list": OpenWebApiEnum.LIST_DEPARTMENT_CHILD,
    "open_web.tenant_department.user.list": OpenWebApiEnum.LIST_DEPARTMENT_USER,
}


class OpenWebApiAuditMiddleware:
    """OpenWeb API 审计中间件"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if api := OPEN_WEB_API_MAP.get(request.resolver_match.url_name):
            self.api = api
            self._create_log(request, response)

        return response

    def _create_log(self, request, response):
        """记录OpenWeb API审计日志"""
        # 直接将审计数据作为 logger 的 extra 参数
        extra = {
            "bk_username": request.user.username,
            "tenant_id": request.META.get("HTTP_X_BK_TENANT_ID", ""),
            "api": self.api,
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
            "object_ids": self._get_object_ids(response),
        }

        logger.info("", extra=extra)

    def _get_result_count(self, response):
        if not status.is_success(response.status_code):
            return 0

        # 请求成功时，提取结果数量
        # 若为 list 分页接口，则返回分页结果数量
        if self.api in [
            OpenWebApiEnum.LIST_VIRTUAL_USER,
        ]:
            return len(response.data["results"])

        # 若为 list 无 count 分页接口，则返回分页结果数量
        if self.api in [
            OpenWebApiEnum.LIST_DEPARTMENT_USER,
        ]:
            return len(response.data)

        # 若为 list 非分页接口，则直接返回结果数量
        if self.api in [
            OpenWebApiEnum.SEARCH_USER,
            OpenWebApiEnum.BATCH_LOOKUP_USER,
            OpenWebApiEnum.SEARCH_DEPARTMENT,
            OpenWebApiEnum.LIST_DEPARTMENT_CHILD,
        ]:
            return len(response.data)

        return 0

    def _get_object_ids(self, response):
        if not status.is_success(response.status_code):
            return []

        # 若为 list 分页接口
        if self.api in [
            OpenWebApiEnum.LIST_VIRTUAL_USER,
        ]:
            return [item["bk_username"] for item in response.data["results"]]

        # 若为 list 无 count 分页接口
        if self.api in [
            OpenWebApiEnum.LIST_DEPARTMENT_USER,
        ]:
            return [item["bk_username"] for item in response.data]

        # 若为 list 非分页接口（部门相关）
        if self.api in [
            OpenWebApiEnum.SEARCH_DEPARTMENT,
            OpenWebApiEnum.LIST_DEPARTMENT_CHILD,
        ]:
            return [item["id"] for item in response.data]

        # 若为 list 非分页接口（用户相关）
        if self.api in [
            OpenWebApiEnum.SEARCH_USER,
            OpenWebApiEnum.BATCH_LOOKUP_USER,
        ]:
            return [item["bk_username"] for item in response.data]

        return []


class TenantIDHeaderMiddleware:
    """租户 ID Header 中间件"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 不开启多租户模式下，不可依赖调用方是否有传递或是否传递正确 TenantID Header
        # 所以这里需要主动设置 TenantID Header 为默认租户
        # 保证后续依赖 TenantID Header 的处理逻辑一致
        if not settings.ENABLE_MULTI_TENANT_MODE:
            request.META["HTTP_X_BK_TENANT_ID"] = BuiltInTenantIDEnum.DEFAULT

        return self.get_response(request)
