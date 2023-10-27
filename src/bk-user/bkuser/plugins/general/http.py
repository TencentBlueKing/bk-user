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
import base64
import logging
from typing import Any, Dict, List

import requests
from django.utils.translation import gettext_lazy as _
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import JSONDecodeError

from bkuser.plugins.general.constants import DEFAULT_PAGE, MAX_TOTAL_COUNT, PAGE_SIZE_FOR_FETCH_FIRST, AuthMethod
from bkuser.plugins.general.exceptions import RequestApiError, RespDataFormatError
from bkuser.plugins.general.models import AuthConfig

logger = logging.getLogger(__name__)


def gen_headers(cfg: AuthConfig) -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}

    if cfg.method == AuthMethod.BEARER_TOKEN:
        # BearerToken
        headers["Authorization"] = f"Bearer {cfg.bearer_token}"
    elif cfg.method == AuthMethod.BASIC_AUTH:
        # BasicAuth
        credentials = base64.b64encode(f"{cfg.username}:{cfg.password}".encode("utf-8")).decode("utf-8")
        headers["Authorization"] = f"Basic {credentials}"

    return headers


def fetch_all_data(
    url: str, headers: Dict[str, str], page_size: int, timeout: int, retries: int
) -> List[Dict[str, Any]]:
    """
    根据指定配置，请求数据源 API 以获取用户 / 部门数据

    :param url: 数据源 URL，如 https://bk.example.com/apis/v1/users
    :param headers: 请求头，包含认证信息等
    :param timeout: 单次请求超时时间
    :param retries: 请求失败重试次数
    :returns: API 返回结果，应符合通用 HTTP 数据源 API 协议
    """
    with requests.Session() as session:
        adapter = HTTPAdapter(
            max_retries=Retry(
                total=retries,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
        )
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        cur_page, max_page = DEFAULT_PAGE, MAX_TOTAL_COUNT / page_size
        total_cnt, items = 0, []
        while True:
            params = {"page": cur_page, "page_size": page_size}
            resp = session.get(url, headers=headers, params=params, timeout=timeout)
            if not resp.ok:
                raise RequestApiError(
                    _("请求数据源 API {} 参数 {} 异常，状态码 {} 响应内容 {}").format(
                        url, params, resp.status_code, resp.content
                    )  # noqa: E501
                )

            try:
                resp_data = resp.json()
            except JSONDecodeError:  # noqa: PERF203
                raise RespDataFormatError(
                    _("数据源 API {} 参数 {} 返回非 Json 格式，响应内容 {}").format(url, params, resp.content)
                )  # noqa: E501

            total_cnt = resp_data.get("count", 0)
            cur_req_results = resp_data.get("results", [])
            items.extend(cur_req_results)

            logger.info(
                "request data source api %s, params %s, get %d items, total count is %d",
                url,
                params,
                len(cur_req_results),
                total_cnt,
            )

            if cur_page * page_size >= total_cnt:
                break

            # 理论拉取数量超过最大上限，强制退出
            if cur_page >= max_page:
                logger.warning("request data source api %s, exceed max page %d, force break...", url, max_page)
                break

            cur_page += 1

    return items


def fetch_first_item(url: str, headers: Dict[str, str], timeout: int) -> Dict[str, Any] | None:
    """
    根据指定配置，请求数据源 API 以获取用户 / 部门第一条数据（测试连通性用）

    :param url: 数据源 URL，如 https://bk.example.com/apis/v1/users
    :param headers: 请求头，包含认证信息等
    :param timeout: 单次请求超时时间
    :returns: API 返回结果，应符合通用 HTTP 数据源 API 协议
    """
    params = {"page": DEFAULT_PAGE, "page_size": PAGE_SIZE_FOR_FETCH_FIRST}
    resp = requests.get(url, headers=headers, params=params, timeout=timeout)
    if not resp.ok:
        raise RequestApiError(
            _("请求数据源 API {} 参数 {} 异常，状态码 {} 响应内容 {}").format(url, params, resp.status_code, resp.content)  # noqa: E501
        )

    try:
        resp_data = resp.json()
    except JSONDecodeError:  # noqa: PERF203
        raise RespDataFormatError(
            _("数据源 API {} 参数 {} 返回非 Json 格式，响应内容 {}").format(url, params, resp.content)
        )  # noqa: E501

    results = resp_data.get("results", [])
    if not results:
        return None

    return results[0]
