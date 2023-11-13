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
from urllib.parse import urljoin, urlparse

from django.conf import settings

from bkuser.common.error_codes import error_codes
from bkuser.common.local import local

from .http import http_get

logger = logging.getLogger("component")


# FIXME: 后续登录OpenAPI接入APIGateway需重新调整
def _call_login_api(http_func, url_path, **kwargs):
    request_id = local.request_id

    kwargs.setdefault("headers", {})
    # 添加默认请求头
    kwargs["headers"].update(
        {
            "Content-Type": "application/json",
            "X-Request-Id": request_id,
        }
    )

    url = urljoin(settings.BK_LOGIN_API_URL, url_path)

    ok, resp_data = http_func(url, **kwargs)
    if not ok:
        logger.error(
            "login api failed! %s %s, kwargs: %s, request_id: %s, error: %s",
            http_func.__name__,
            url,
            kwargs,
            request_id,
            resp_data["error"],
        )
        raise error_codes.REMOTE_REQUEST_ERROR.format(
            f"request login fail! "
            f"Request=[{http_func.__name__} {urlparse(url).path} request_id={request_id}]"
            f"error={resp_data['error']}"
        )

    return resp_data["data"]


def verify_bk_token(bk_token: str):
    """验证bk_token"""
    url_path = "/api/v1/is_login/"
    return _call_login_api(http_get, url_path, params={"bk_token": bk_token})


def get_user_info(bk_token: str):
    """
    获取用户信息
    """
    url_path = "/api/v1/get_user/"
    return _call_login_api(http_get, url_path, params={"bk_token": bk_token})
