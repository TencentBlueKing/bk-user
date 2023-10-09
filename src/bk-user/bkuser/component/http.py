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
import time
from urllib.parse import urlparse

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter

logger = logging.getLogger("component")
# 定义慢请求耗时，单位毫秒
SLOW_REQUEST_LATENCY = 100

session = requests.Session()
adapter = HTTPAdapter(pool_connections=settings.REQUESTS_POOL_CONNECTIONS, pool_maxsize=settings.REQUESTS_POOL_MAXSIZE)
session.mount("https://", adapter)
session.mount("http://", adapter)


def _http_request(method, url, **kwargs):
    # 添加JSON Header
    headers = kwargs.get("headers") or {}
    headers.update({"Content-Type": "application/json"})
    kwargs["headers"] = headers

    # 默认30秒超时
    if "timeout" not in kwargs:
        kwargs["timeout"] = 30

    # 默认不校验证书
    if "verify" not in kwargs:
        kwargs["verify"] = False

    st = time.time()

    if method not in ["GET", "POST", "DELETE", "PUT", "PATCH", "HEAD"]:
        return False, {"error": "method not supported"}

    try:
        resp = session.request(method, url, **kwargs)
    except requests.exceptions.RequestException as e:
        logger.exception("http request error! %s %s, kwargs: %s", method, url, kwargs)
        return False, {"error": str(e)}
    else:
        # record
        latency = int((time.time() - st) * 1000)
        # greater than 100ms
        if latency > SLOW_REQUEST_LATENCY:
            logger.warning("http slow request! method: %s, url: %s, latency: %dms", method, url, latency)

        # 状态非20x，说明是异常请求
        if not (200 <= resp.status_code <= 299):  # noqa: PLR2004
            content = resp.content[:256] if resp.content else ""
            logger.error(
                "http request fail! %s %s, kwargs: %s, response.status_code: %s, response.body: %s",
                method,
                url,
                str(kwargs),
                resp.status_code,
                content,
            )

            return False, {
                "error": (
                    f"status_code is {resp.status_code}, not 20x! "
                    f"{method} {urlparse(url).path}, resp.body={content}"
                )
            }

        try:
            return True, resp.json()
        except Exception as e:
            logger.exception("http response body not json! %s %s, kwargs: %s", method, url, kwargs)
            return False, {"error": str(e)}


def http_get(url, **kwargs):
    return _http_request(method="GET", url=url, **kwargs)


def http_post(url, **kwargs):
    return _http_request(method="POST", url=url, **kwargs)


def http_put(url, **kwargs):
    return _http_request(method="PUT", url=url, **kwargs)


def http_patch(url, **kwargs):
    return _http_request(method="PATCH", url=url, **kwargs)


def http_delete(url, **kwargs):
    return _http_request(method="DELETE", url=url, **kwargs)
