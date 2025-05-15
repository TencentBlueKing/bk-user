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
from urllib.parse import urlparse

from django.conf import settings

from bkuser.common.error_codes import error_codes
from bkuser.common.local import local
from bkuser.utils.url import urljoin

logger = logging.getLogger("component.apigw")


def _call_apigw_api(http_func, apigw_name, url_path, **kwargs):
    request_id = local.request_id
    if "headers" not in kwargs:
        kwargs["headers"] = {}

    # 应用认证&用户认证Header
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

    # 添加默认请求头
    kwargs["headers"].update(
        {
            "Content-Type": "application/json",
            "X-Request-Id": request_id,
            "X-Bkapi-Authorization": json.dumps(bkapi_authorization),
            "X-Bk-Tenant-Id": local.request.user.get_property("tenant_id"),
        }
    )

    apigw_url = urljoin(settings.BK_API_URL_TMPL.format(api_name=apigw_name), "/prod")
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
        raise error_codes.REMOTE_REQUEST_ERROR.format(
            f"request apigw fail! "
            f"Request=[{http_func.__name__} {urlparse(url).path} request_id={request_id}]"
            f"error={resp_data['error']}"
        )
    return resp_data["data"]
