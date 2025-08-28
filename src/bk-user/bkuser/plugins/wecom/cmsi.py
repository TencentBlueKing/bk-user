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

import json
import logging
from typing import Any, Dict
from urllib.parse import urlparse

from django.conf import settings

from bkuser.plugins.common import local
from bkuser.plugins.http import http_get
from bkuser.plugins.utils import scrub_data, urljoin
from bkuser.plugins.wecom.exceptions import RequestAPIError

logger = logging.getLogger(__name__)


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
            scrub_data(kwargs, custom_fields=["X-Bkapi-Authorization", "X-Request-Id"]),
            request_id,
            resp_data["error"],
        )
        raise RequestAPIError(
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
        scrub_data(kwargs, custom_fields=["X-Bkapi-Authorization", "X-Request-Id"]),
        request_id,
        code,
        message,
    )

    raise RequestAPIError(
        f"request esb error! "
        f"Request=[{http_func.__name__} {urlparse(url).path} request_id={request_id}] "
        f"Response[code={code}, message={message}]"
    )


def _call_apigw_api(http_func, apigw_name, url_path, tenant_id, **kwargs):
    request_id = local.request_id
    kwargs.setdefault("headers", {})

    # 应用认证 Header
    bkapi_authorization = {
        "bk_app_code": settings.BK_APP_CODE,
        "bk_app_secret": settings.BK_APP_SECRET,
    }

    # 添加默认请求头
    kwargs["headers"].update(
        {
            "Content-Type": "application/json",
            "X-Request-Id": request_id,
            "X-Bkapi-Authorization": json.dumps(bkapi_authorization),
            "X-Bk-Tenant-Id": tenant_id,
        }
    )

    apigw_url = urljoin(settings.BK_API_URL_TMPL.format(api_name=apigw_name), settings.BK_CMSI_APIGW_STAGE)
    url = urljoin(apigw_url, url_path)

    ok, resp_data = http_func(url, **kwargs)
    if not ok:
        logger.error(
            "apigw api failed! %s %s, request_id: %s, error: %s",
            http_func.__name__,
            url,
            request_id,
            resp_data["error"],
        )
        raise RequestAPIError(
            f"request apigw fail! "
            f"Request=[{http_func.__name__} {urlparse(url).path} request_id={request_id}]"
            f"error={resp_data['error']}"
        )
    return resp_data["data"]


def get_wecom_config(tenant_id: str) -> Dict[str, Any]:
    """获取蓝鲸 CMSI 中的微信配置"""
    if settings.ENABLE_MULTI_TENANT_MODE:
        return _call_apigw_api(http_get, "bk-cmsi", "/v1/channels/weixin/settings/", tenant_id)
    return _call_esb_api(http_get, "/api/c/compapi/esb/get_weixin_config/")


def get_access_token_from_cmsi(tenant_id: str) -> str:
    """从蓝鲸 CMSI 获取 access_token"""
    if settings.ENABLE_MULTI_TENANT_MODE:
        resp_data = _call_apigw_api(http_get, "bk-cmsi", "/v1/channels/weixin/token/", tenant_id)
    else:
        resp_data = _call_esb_api(http_get, "/api/c/compapi/weixin/get_token/")

    return resp_data["access_token"]
