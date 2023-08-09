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
from urllib.parse import urljoin, urlparse

from django.conf import settings

from bkuser.common.error_codes import error_codes
from bkuser.common.local import local

logger = logging.getLogger("component")


def _call_esb_api(http_func, url_path, **kwargs):
    request_id = local.request_id
    if "headers" not in kwargs:
        kwargs["headers"] = {}

    # 应用认证&用户认证Header
    # Note: 特殊逻辑，如果参数有bk_token，则使用，没有则使用bk_username认证
    bk_token = (
        kwargs.get("params", {}).get("bk_token")
        or kwargs.get("data", {}).get("bk_token")
        or kwargs.get("json", {}).get("bk_token")
    )
    bkapi_authorization = {
        "bk_app_code": settings.BK_APP_CODE,
        "bk_app_secret": settings.BK_APP_SECRET,
    }
    if bk_token:
        bkapi_authorization["bk_token"] = bk_token
    else:
        bkapi_authorization["bk_username"] = "admin"  # 存在后台任务，无法使用登录态的方式

    # 添加默认请求头
    kwargs["headers"].update(
        {
            "Content-Type": "application/json",
            "X-Request-Id": request_id,
            "X-Bkapi-Authorization": json.dumps(bkapi_authorization),
        }
    )

    url = urljoin(settings.BK_COMPONENT_API_URL, url_path)

    ok, resp_data = http_func(url, **kwargs)
    if not ok:
        logger.error(
            "esb api failed! %s %s, kwargs: %s, request_id: %s, error: %s",
            http_func.__name__,
            url,
            kwargs,  # TODO: 移除敏感信息
            request_id,
            resp_data["error"],
        )
        raise error_codes.REMOTE_REQUEST_ERROR.format(
            f"request esb fail! "
            f"Request=[{http_func.__name__} {urlparse(url).path} request_id={request_id}]"
            f"error={resp_data['error']}"
        )

    code = resp_data.get("code", -1)
    message = resp_data.get("message", "unknown")

    # code may be string or int, and login v1 the code is "00"
    try:
        code = int(code)
    except Exception:  # pylint: disable=broad-except
        pass
    if code in ("0", 0, "00"):
        return resp_data["data"]

    logger.error(
        "esb api error! %s %s, data: %s, request_id: %s, code: %s, message: %s",
        http_func.__name__,
        url,
        kwargs,  # TODO: 移除敏感信息
        local.request_id,
        code,
        message,
    )

    raise error_codes.REMOTE_REQUEST_ERROR.format(
        f"request esb error! "
        f"Request=[{http_func.__name__} {urlparse(url).path} request_id={request_id}] "
        f"Response[code={code}, message={message}]"
    )
