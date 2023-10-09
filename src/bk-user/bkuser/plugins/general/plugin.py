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

from bkuser.plugins.base import BaseDataSourcePlugin
from bkuser.plugins.general.constants import AuthMethod
from bkuser.plugins.general.exceptions import RequestApiError, RespDataFormatError
from bkuser.plugins.general.http import fetch_all_data, fetch_first_item
from bkuser.plugins.general.models import GeneralDataSourcePluginConfig
from bkuser.plugins.models import (
    RawDataSourceDepartment,
    RawDataSourceUser,
    TestConnectionResult,
)

logger = logging.getLogger(__name__)


class GeneralDataSourcePlugin(BaseDataSourcePlugin):
    """通用 HTTP 数据源插件"""

    config_class = GeneralDataSourcePluginConfig

    def __init__(self, plugin_config: GeneralDataSourcePluginConfig):
        self.plugin_config = plugin_config

    def fetch_departments(self) -> List[RawDataSourceDepartment]:
        """获取部门信息"""
        cfg = self.plugin_config.server_config
        depts = fetch_all_data(
            cfg.server_base_url + cfg.department_api_path,
            self._gen_headers(),
            cfg.request_timeout,
            cfg.retries,
        )
        return [self._gen_raw_dept(d) for d in depts]

    def fetch_users(self) -> List[RawDataSourceUser]:
        """获取用户信息"""
        cfg = self.plugin_config.server_config
        users = fetch_all_data(
            cfg.server_base_url + cfg.user_api_path,
            self._gen_headers(),
            cfg.request_timeout,
            cfg.retries,
        )
        return [self._gen_raw_user(u) for u in users]

    def test_connection(self) -> TestConnectionResult:
        """连通性测试"""
        cfg = self.plugin_config.server_config
        err_msg, user_data, user, dept_data, dept = "", None, None, None, None
        try:
            user_data = fetch_first_item(
                cfg.server_base_url + cfg.user_api_path,
                self._gen_headers(),
                cfg.request_timeout,
            )

            dept_data = fetch_first_item(
                cfg.server_base_url + cfg.department_api_path,
                self._gen_headers(),
                cfg.request_timeout,
            )

        except (RequestApiError, RespDataFormatError) as e:
            err_msg = str(e)
        except Exception as e:
            logger.exception("general data source plugin test connection error")
            err_msg = str(e)

        if user_data and dept_data:
            # FIXME (su) 捕获并进行异常处理，提示错误信息给到用户
            user = self._gen_raw_user(user_data)
            dept = self._gen_raw_dept(dept_data)

        return TestConnectionResult(error_message=err_msg, user=user, department=dept)

    def _gen_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}

        cfg = self.plugin_config.auth_config
        if cfg.method == AuthMethod.BEARER_TOKEN:
            # BearerToken
            headers["Authorization"] = f"Bearer {cfg.bearer_token}"
        elif cfg.method == AuthMethod.BASIC_AUTH:
            # BasicAuth
            credentials = base64.b64encode(f"{cfg.username}:{cfg.password}".encode("utf-8")).decode("utf-8")
            headers["Authorization"] = f"Basic {credentials}"

        return headers

    @staticmethod
    def _gen_raw_user(user: Dict[str, Any]) -> RawDataSourceUser:
        return RawDataSourceUser(
            code=user["id"],
            properties={
                "username": user["username"],
                "full_name": user["full_name"],
                "email": user["email"],
                "phone": user["phone"],
                "phone_country_code": user["phone_country_code"],
                **user["extras"],
            },
            leaders=user["leaders"],
            departments=user["departments"],
        )

    @staticmethod
    def _gen_raw_dept(dept: Dict[str, Any]) -> RawDataSourceDepartment:
        return RawDataSourceDepartment(
            code=dept["id"],
            name=dept["name"],
            parent=dept["parent"],
        )
