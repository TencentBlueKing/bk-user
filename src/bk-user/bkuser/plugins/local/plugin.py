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
from typing import List

from django.utils.translation import gettext_lazy as _
from openpyxl.workbook import Workbook

from bkuser.plugins.base import BaseDataSourcePlugin
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig
from bkuser.plugins.local.parser import LocalDataSourceDataParser
from bkuser.plugins.models import (
    RawDataSourceDepartment,
    RawDataSourceUser,
    TestConnectionResult,
)


class LocalDataSourcePlugin(BaseDataSourcePlugin):
    """本地数据源插件"""

    id = DataSourcePluginEnum.LOCAL
    config_class = LocalDataSourcePluginConfig

    def __init__(self, plugin_config: LocalDataSourcePluginConfig, workbook: Workbook):
        self.plugin_config = plugin_config
        self.workbook = workbook
        self.parser = LocalDataSourceDataParser(self.workbook)

    def fetch_departments(self) -> List[RawDataSourceDepartment]:
        """获取部门信息"""
        if not self.parser.is_parsed:
            self.parser.parse()

        return self.parser.get_departments()

    def fetch_users(self) -> List[RawDataSourceUser]:
        """获取用户信息"""
        if not self.parser.is_parsed:
            self.parser.parse()

        return self.parser.get_users()

    def test_connection(self) -> TestConnectionResult:
        raise NotImplementedError(_("本地数据源不支持连通性测试"))
