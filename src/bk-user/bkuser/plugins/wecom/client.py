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
from typing import Any, Dict, List

import requests
from requests.adapters import HTTPAdapter, Retry

from bkuser.plugins.http import _call_bk_user_api, http_get_20x
from bkuser.plugins.utils import urljoin
from bkuser.plugins.wecom.constants import WECOM_API_BASE_URL, WeComDataType, WeComUserStatus
from bkuser.plugins.wecom.exceptions import RequestAPIError
from bkuser.plugins.wecom.models import ServerConfig

logger = logging.getLogger(__name__)


class WeComAPIClient:
    """企业微信API客户端"""

    def __init__(self, server_config: ServerConfig, context: Dict[str, Any]):
        self.server_config = server_config
        self.context = context

    @property
    def access_token(self) -> str:
        """获取企业微信 access_token"""
        # 从插件配置的上下文中获取 tenant_id
        tenant_id = self.context.get("tenant_id")

        # 从用户管理中调用 API 获取 access_token
        resp = _call_bk_user_api(
            http_get_20x,
            url_path="/api/v3/plugin/wecom/access-token/",
            params={
                "corp_id": self.server_config.corp_id,
                "corp_secret": self.server_config.corp_secret,
                "tenant_id": tenant_id,
            },
        )
        return resp["access_token"]

    def _call(self, url_path: str, params: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """调用企业微信接口"""
        url = urljoin(WECOM_API_BASE_URL, url_path)
        with requests.Session() as session:
            adapter = HTTPAdapter(
                max_retries=Retry(
                    total=self.server_config.retries,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                )
            )
            session.mount("https://", adapter)

            resp = session.get(url, timeout=self.server_config.request_timeout, params=params, **kwargs)
            if not resp.ok:
                raise RequestAPIError(
                    f"request wecom api fail! Request=[GET {url}] "
                    f"status_code={resp.status_code}, content={resp.text}"
                )

            resp_data = resp.json()

            errcode = resp_data.get("errcode") or 0
            # 出错返回码，为 0 表示成功，非 0 表示调用失败
            if not errcode:
                return resp_data

            errmsg = resp_data.get("errmsg", "unknown")
            raise RequestAPIError(
                f"request wecom api error! " f"Request=[GET {url}] Response[code={errcode}, message={errmsg}]"
            )

    def fetch_department_list(self) -> List[int]:
        """获取子部门 ID 列表"""
        resp_data = self._call(
            "/department/simplelist",
            params={"access_token": self.access_token, "id": self.server_config.sync_dept_id},
        )

        dept_list = resp_data.get("department_id", [])

        return [dept_info["id"] for dept_info in dept_list]

    def fetch_department_info(self, id: int) -> Dict[str, Any]:
        """获取部门信息"""
        resp_data = self._call("/department/get", params={"access_token": self.access_token, "id": id})
        return resp_data.get("department", {})

    def fetch_user_info(self, department_id: int) -> List[Dict[str, Any]]:
        """获取部门所属用户信息"""
        resp_data = self._call(
            "/user/list", params={"access_token": self.access_token, "department_id": department_id}
        )
        users = resp_data.get("userlist", [])

        result = []
        for user in users:
            # 只获取激活企业微信的用户
            if str(user["status"]) != WeComUserStatus.ACTIVE:
                continue

            result.append(user)

        return result

    def fetch_first_item(self, data_type: str, dept_ids: List[int]) -> Dict[str, Any] | None:
        """获取第一条数据"""
        if data_type == WeComDataType.DEPARTMENT:
            return self.fetch_department_info(dept_ids[0])

        if data_type == WeComDataType.USER:
            for dept_id in dept_ids:
                if user_data := self.fetch_user_info(dept_id):
                    return user_data[0]

        return None

    def fetch_all_data(self, data_type: str, dept_ids: List[int]) -> List[Dict[str, Any]]:
        """获取所有数据"""
        if data_type == WeComDataType.DEPARTMENT:
            return [self.fetch_department_info(dept_id) for dept_id in dept_ids]

        if data_type == WeComDataType.USER:
            # 收集所有用户，然后根据 userid 去重
            all_users = []
            user_ids: set[str] = set()

            for dept_id in dept_ids:
                users = self.fetch_user_info(dept_id)
                for user in users:
                    if user["userid"] not in user_ids:
                        user_ids.add(user["userid"])
                        all_users.append(user)

            return all_users

        return []
