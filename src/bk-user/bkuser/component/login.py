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
from urllib.parse import urlparse

from django.conf import settings

from bkuser.common.error_codes import error_codes
from bkuser.common.local import local
from bkuser.utils.url import urljoin

from .http import http_get

logger = logging.getLogger("component")


# Note: 用户管理模块的调用登录接口，不经过 APIGateway，避免循环依赖
def _call_login_api(http_func, url_path, **kwargs):
    request_id = local.request_id

    kwargs.setdefault("headers", {})
    # 添加默认请求头
    kwargs["headers"].update(
        {
            "Content-Type": "application/json",
            "X-Request-Id": request_id,
            "X-Bk-App-Code": settings.BK_APP_CODE,
            "X-Bk-App-Secret": settings.BK_APP_SECRET,
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


def get_user_info(bk_token: str):
    """
    获取用户信息
    """
    url_path = "api/v3/bkuser/bk-tokens/userinfo/"
    return _call_login_api(http_get, url_path, params={"bk_token": bk_token})
