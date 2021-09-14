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
            raise CustomAPIRequestFailed()

        try:
            return resp.json().get("results", [])
        except Exception as e:
            logger.exception("failed to parse resp as json, cUrl format: %s", curl_format)
            raise CustomAPIRequestFailed() from e

    def fetch_profiles(self, page_info: Optional[PageInfo] = None) -> CustomTypeList:
        """获取 profile 对象列表"""
        results = self._fetch_items(path=self.paths["profile"])
        return CustomTypeList.from_list([CustomProfile.from_dict(x) for x in results])

    def fetch_departments(self, page_info: Optional[PageInfo] = None) -> CustomTypeList:
        """获取 department 对象列表"""
        results = self._fetch_items(path=self.paths["department"])
        return CustomTypeList.from_list([CustomDepartment.from_dict(x) for x in results])
