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

from django.utils.translation import gettext_lazy as _

from bkuser.plugins.base import BaseDataSourcePlugin, PluginLogger
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.models import RawDataSourceDepartment, RawDataSourceUser, TestConnectionResult
from bkuser.plugins.wecom.client import WeComAPIClient
from bkuser.plugins.wecom.constants import WeComDataType
from bkuser.plugins.wecom.exceptions import RequestAPIError
from bkuser.plugins.wecom.models import WeComDataSourcePluginConfig

logger = logging.getLogger(__name__)


class WeComDataSourcePlugin(BaseDataSourcePlugin):
    """企业微信数据源插件"""

    id = DataSourcePluginEnum.WECOM
    config_class = WeComDataSourcePluginConfig

    def __init__(self, plugin_config: WeComDataSourcePluginConfig, logger: PluginLogger):
        self.logger = logger
        self.client = WeComAPIClient(plugin_config.server_config, plugin_config.context)
        self._cached_dept_ids: List[int] = []

    def fetch_departments(self) -> List[RawDataSourceDepartment]:
        """获取部门信息"""
        self._cached_dept_ids = self.client.fetch_department_list()
        depts = self.client.fetch_all_data(WeComDataType.DEPARTMENT, self._cached_dept_ids)
        return [self._gen_raw_dept(d) for d in depts]

    def fetch_users(self) -> List[RawDataSourceUser]:
        """获取用户信息"""
        if not self._cached_dept_ids:
            self._cached_dept_ids = self.client.fetch_department_list()

        users = self.client.fetch_all_data(WeComDataType.USER, self._cached_dept_ids)
        return [self._gen_raw_user(u) for u in users]

    def test_connection(self) -> TestConnectionResult:
        """测试连接"""
        err_msg, user, dept = "", None, None
        user_data, dept_data = None, None

        try:
            dept_ids = self.client.fetch_department_list()
            if not dept_ids:
                err_msg = _("获取到的部门列表为空，请检查企业微信配置")
                return TestConnectionResult(error_message=err_msg)

            dept_data = self.client.fetch_first_item(WeComDataType.DEPARTMENT, dept_ids)
            user_data = self.client.fetch_first_item(WeComDataType.USER, dept_ids)
        except RequestAPIError as e:
            err_msg = str(e)
        except Exception as e:
            logger.exception("wecom data source plugin test connection error")
            err_msg = _("连接测试失败: 无法连接企业微信服务，请检查 corp_id 和 corp_secret 配置。异常信息：{}").format(
                str(e)
            )

        # 请求 API 有异常，直接返回
        if err_msg:
            return TestConnectionResult(error_message=err_msg)

        # 检查获取到的数据情况，若都没有数据，也是异常
        if not (dept_data and user_data):
            err_msg = _("获取到的企业微信部门/用户数据为空，请检查企业微信服务配置")
        else:
            try:
                dept = self._gen_raw_dept(dept_data)
                user = self._gen_raw_user(user_data)
            except Exception as e:
                err_msg = _("解析企业微信数据失败，请检查返回的数据格式。异常信息：{}").format(str(e))

        return TestConnectionResult(
            error_message=str(err_msg),
            user=user,
            department=dept,
            extras={"user_data": user_data, "department_data": dept_data},
        )

    def _gen_raw_dept(self, dept: Dict[str, Any]) -> RawDataSourceDepartment:
        return RawDataSourceDepartment(
            code=str(dept["id"]),
            name=dept["name"],
            parent=str(dept["parentid"]) if dept["parentid"] else None,
        )

    def _gen_raw_user(self, user: Dict[str, Any]) -> RawDataSourceUser:
        return RawDataSourceUser(
            code=user["userid"],
            properties={
                "username": user["userid"],
                "full_name": user["name"],
            },
            leaders=[str(leader) for leader in user["direct_leader"]],
            departments=[str(dept_id) for dept_id in user["department"]],
        )
