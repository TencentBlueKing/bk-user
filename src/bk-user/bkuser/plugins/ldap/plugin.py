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
from typing import List

from ldap3 import SAFE_SYNC, Connection, Server

from bkuser.plugins.base import BaseDataSourcePlugin, PluginLogger
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.ldap.models import LDAPDataSourcePluginConfig
from bkuser.plugins.models import RawDataSourceDepartment, RawDataSourceUser, TestConnectionResult

logger = logging.getLogger(__name__)


class LDAPDataSourcePlugin(BaseDataSourcePlugin):
    """LDAP 数据源插件"""

    id = DataSourcePluginEnum.LDAP
    config_class = LDAPDataSourcePluginConfig

    def __init__(self, plugin_config: LDAPDataSourcePluginConfig, logger: PluginLogger):
        self.plugin_config = plugin_config
        self.logger = logger
        self.conn: Connection | None = None

    def fetch_departments(self) -> List[RawDataSourceDepartment]:
        """获取部门信息"""
        return []

    def fetch_users(self) -> List[RawDataSourceUser]:
        """获取用户信息"""
        return []

    def test_connection(self) -> TestConnectionResult:
        """连通性测试"""
        return TestConnectionResult(error_message="")

    def _get_conn(self) -> Connection:
        if not self.conn:
            self.conn = Connection(
                server=Server(self.plugin_config.server_config.server_url),
                user=self.plugin_config.server_config.bind_dn,
                password=self.plugin_config.server_config.bind_password,
                client_strategy=SAFE_SYNC,
            )

        return self.conn
