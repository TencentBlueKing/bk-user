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
from typing import Optional

import requests
from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import get_language
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from bkuser_global.local import local

logger = logging.getLogger(__name__)


def make_proxy_headers(username: str) -> dict:
    return {
        "X-BkUser-Operator": username,
        "X-Bk-App-Code": settings.APP_ID,
        "X-Bk-App-Secret": settings.APP_TOKEN,
        "Accept-Language": get_language(),
        "X-Request-ID": local.request_id,
    }


class BkUserApiProxy(GenericViewSet):
    """do the proxy from saas to api
    should be removed when we remove saas totally
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @staticmethod
    def get_client_ip(request) -> Optional[str]:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]

        for h in ["REMOTE_ADDR", "X-Real-IP"]:
            ip = request.META.get(h)
            if ip:
                return ip
        return ""

    def do_proxy(self, request, rewrite_path=None):
        print("do_proxy")
        try:
            return self.do_call(request, rewrite_path)
        except Exception as e:
            logger.exception("do proxy error")
            return HttpResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=str(e),
            )

    def get_api_path(self, request) -> str:
        """获取真实 API Path"""
        if settings.SITE_URL == "/":
            return request.path

        return "/" + request.path.replace(settings.SITE_URL, "")

    def do_call(self, request, rewrite_path=None):
        print("do_call")
        method = request.method
        path = self.get_api_path(request)
        if rewrite_path:
            path = rewrite_path

        url = settings.BK_USER_CORE_API_HOST + path
        params = request.GET.copy()
        data = request.body

        headers = make_proxy_headers(request.user.username)
        ip = self.get_client_ip(request)
        if ip:
            headers.update({settings.CLIENT_IP_FROM_SAAS_HEADER: ip})

        resp = requests.request(method, url, params=params, data=data, headers=headers)

        return HttpResponse(
            resp.content,
            status=resp.status_code,
            content_type="application/json",
        )
