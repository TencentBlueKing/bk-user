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
from dataclasses import dataclass
from typing import Optional

import curlify
import requests

from bkuser_core.categories.plugins.custom.exceptions import CustomAPIRequestFailed
from bkuser_core.categories.plugins.custom.models import CustomDepartment, CustomProfile, CustomTypeList
from bkuser_core.user_settings.loader import ConfigProvider

logger = logging.getLogger(__name__)


@dataclass
class PageInfo:
    page: int
    page_size: int


@dataclass
class CustomDataClient:
    category_id: int
    api_host: str
    paths: dict

    @classmethod
    def from_config(cls):
        """从配置中创建客户端"""

    def __post_init__(self):
        self.config_loader = ConfigProvider(self.category_id)

    def _fetch_items(self, path: str):
        url = "/".join(s.strip("/") for s in [self.api_host, path])
        resp = requests.get(url, timeout=30)

        curl_format = curlify.to_curl(resp.request)
        logger.debug("going to call: %s", url)
        if resp.status_code >= 400:
            logger.error(
                "failed to request api, status code: %s cUrl format: %s",
                resp.status_code,
                curl_format,
            )
            raise CustomAPIRequestFailed(f"failed to request api, status code: {resp.status_code}")

        try:
            resp_body = resp.json()
        except Exception as e:
            logger.exception("failed to parse resp as json, cUrl format: %s", curl_format)
            raise CustomAPIRequestFailed("failed to parse resp as json") from e

        # results not present in response body
        if "results" not in resp_body:
            logger.error("no `results` in response, cUrl format: %s", curl_format)
            raise CustomAPIRequestFailed("there got no `results` in response body")

        results = resp_body.get("results", [])
        # results not a list
        if not isinstance(results, list):
            logger.error("`results` in response is not a list, cUrl format: %s", curl_format)
            raise CustomAPIRequestFailed("the `results` in response is not a list")

        # currently, if the results is empty, CustomTypeList.custom_type will raise IndexError(task fail)
        # so, here, we should check here: results size should not be empty
        if not results:
            logger.error("`results` in response is empty, cUrl format: %s", curl_format)
            raise CustomAPIRequestFailed("the `results` in response is empty")

        return results

    def fetch_profiles(self, page_info: Optional[PageInfo] = None) -> CustomTypeList:
        """获取 profile 对象列表"""
        results = self._fetch_items(path=self.paths["profile"])
        return CustomTypeList.from_list([CustomProfile.from_dict(x) for x in results])

    def fetch_departments(self, page_info: Optional[PageInfo] = None) -> CustomTypeList:
        """获取 department 对象列表"""
        results = self._fetch_items(path=self.paths["department"])
        return CustomTypeList.from_list([CustomDepartment.from_dict(x) for x in results])
