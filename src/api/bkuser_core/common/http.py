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
from typing import TYPE_CHECKING, Dict, Optional

from django.conf import settings

if TYPE_CHECKING:
    from django.http import HttpRequest
    from rest_framework.response import Response

# FIXME: 重构这里, 避免复杂的处理逻辑

logger = logging.getLogger(__name__)


def _force_response_data(resp: "Response", force_data: Optional[Dict]) -> "Response":
    """强制刷返回值"""
    # 来自缓存的 response 没有对应属性
    # 由于 response 已经被渲染，并不需要 callback
    if not getattr(resp, "_post_render_callbacks", None):
        resp._post_render_callbacks = []

    resp.data = force_data
    resp._is_rendered = False

    # templateResponse has no render, which we won't care
    if not getattr(resp, "render", False):
        return resp

    resp.render()
    return resp


def force_response_ee_format(resp: "Response") -> "Response":
    """强制返回值企业版格式"""
    if is_response_ee_format(resp):
        return resp

    return _force_response_data(
        resp,
        {"result": True, "code": 0, "message": "success", "data": getattr(resp, "data", None)},
    )


def force_response_raw_format(resp: "Response") -> "Response":
    """强制返回值原生请求"""
    if not is_response_ee_format(resp):
        return resp

    return _force_response_data(resp, resp.data.get("data", None))


def is_response_ee_format(resp: "Response") -> bool:
    """返回值是否符合企业版格式"""
    if getattr(resp, "data", None) is None:
        return False

    required_keys = ["result", "message", "code", "data"]
    for key in required_keys:
        if key not in resp.data:
            return False

    return True


def exist_force_raw_header(request: "HttpRequest") -> bool:
    """通过 Header 判断是否使用原生格式"""
    return bool(request.META.get(settings.FORCE_RAW_RESPONSE_HEADER))


def should_use_raw_response(req: "HttpRequest", resp: "Response") -> bool:
    """是否应该使用原生格式返回"""
    # 非 API 请求不包装返回值
    # NOTE: 目前有环境调用/api/v2/profiles/用到通过header强制使用raw response, 所以暂时不能去掉

    if not req.path.startswith("/api/"):
        return True

    # 是否强制使用原生格式
    if exist_force_raw_header(req):
        return True

    return False
