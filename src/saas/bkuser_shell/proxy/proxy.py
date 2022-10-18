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


session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=settings.REQUESTS_POOL_CONNECTIONS, pool_maxsize=settings.REQUESTS_POOL_MAXSIZE
)
session.mount("https://", adapter)
session.mount("http://", adapter)


class BkUserApiProxy(GenericViewSet):
    """do the proxy from saas to api
    should be removed when we remove saas totally
    """

    # 校验登录态
    permission_classes = [
        IsAuthenticated,
    ]

    @staticmethod
    def _get_client_ip(request) -> Optional[str]:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]

        for h in ["REMOTE_ADDR", "X-Real-IP"]:
            ip = request.META.get(h)
            if ip:
                return ip
        return ""

    @staticmethod
    def get_api_path(request) -> str:
        """获取真实 API Path"""
        if settings.SITE_URL == "/":
            return request.path

        return "/" + request.path.replace(settings.SITE_URL, "").lstrip("/")

    def do_proxy(self, request, rewrite_path=None):
        try:
            return self._do_call(request, rewrite_path)
        except Exception as e:
            logger.exception("do proxy error")
            return HttpResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=str(e),
            )

    def _do_call(self, request, rewrite_path=None):
        method = request.method
        path = self.get_api_path(request)
        if rewrite_path:
            path = rewrite_path

        url = settings.BK_USER_CORE_API_HOST + path
        params = request.GET.copy()
        data = request.data
        # NOTE: can't read this, because drf readed it
        # data = request.body

        # make headers
        headers = make_proxy_headers(request.user.username)
        headers["Content-Type"] = request.headers.get("Content-Type", "application/json")

        ip = self._get_client_ip(request)
        if ip:
            headers.update({settings.CLIENT_IP_FROM_SAAS_HEADER: ip})

        # do call
        if "application/json" in request.headers.get("Content-Type", "application/json"):
            # for json
            resp = session.request(method, url, params=params, json=data, headers=headers)
        else:
            # for file upload and others
            if "file_name" in data:
                file_name = data.pop("file_name")
                # 应对excel 文件名是中文的情况
                file_name = file_name[0].encode()
                headers["Content-Disposition"] = f"attachment; filename={file_name}"

            files = None
            file = data.get("file", None)
            if file:
                data.pop("file")
                files = {"file": file}
            resp = session.request(method, url, params=params, data=data, headers=headers, files=files)

        content = resp.content
        status_code = resp.status_code

        # 无权限, 改状态码为403
        if b"auth_infos" in content and b"callback_url" in content:
            status_code = status.HTTP_403_FORBIDDEN

        resp_headers = resp.headers
        if "Content-Encoding" in resp_headers:
            resp_headers.pop("Content-Encoding")

        logger.debug(
            "proxy request[method=%s,url=%s,params=%s,data=%s,headers=%s] response[status=%s,headers=%s,content=%s]",
            method,
            url,
            params,
            data,
            headers,
            status_code,
            content,
            resp_headers,
        )

        # DONT'T set the content_type here!
        return HttpResponse(
            content,
            status=status_code,
            headers=resp_headers,
        )
