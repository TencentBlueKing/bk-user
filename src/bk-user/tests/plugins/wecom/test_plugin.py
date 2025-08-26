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

import pytest
from bkuser.plugins.models import RawDataSourceDepartment, RawDataSourceUser
from bkuser.plugins.wecom.plugin import WeComDataSourcePlugin


class TestWeComDataSourcePlugin:
    """测试企业微信数据源插件"""

    @pytest.mark.usefixtures("_mock_wecom_client")
    def test_fetch_departments(self, wecom_ds_cfg, logger):
        """测试获取部门信息"""
        plugin = WeComDataSourcePlugin(wecom_ds_cfg, logger)
        departments = plugin.fetch_departments()

        assert len(departments) == 5

        assert departments[0] == RawDataSourceDepartment(
            code="1",
            name="总公司",
            parent=None,  # parentid=0 表示顶级部门
        )

        assert departments[1] == RawDataSourceDepartment(
            code="2",
            name="技术部",
            parent="1",
        )

        assert departments[3] == RawDataSourceDepartment(
            code="4",
            name="前端团队",
            parent="2",
        )

    @pytest.mark.usefixtures("_mock_wecom_client")
    def test_fetch_users(self, wecom_ds_cfg, logger):
        """测试获取用户信息"""
        plugin = WeComDataSourcePlugin(wecom_ds_cfg, logger)
        users = plugin.fetch_users()

        assert len(users) == 3

        assert users[0] == RawDataSourceUser(
            code="zhangsan",
            properties={
                "username": "zhangsan",
                "full_name": "张三",
            },
            leaders=[],
            departments=["1"],
        )

        assert users[1] == RawDataSourceUser(
            code="lisi",
            properties={
                "username": "lisi",
                "full_name": "李四",
            },
            leaders=["zhangsan"],
            departments=["2", "4"],
        )

        assert users[2] == RawDataSourceUser(
            code="wangwu",
            properties={
                "username": "wangwu",
                "full_name": "王五",
            },
            leaders=["zhangsan"],
            departments=["5"],
        )

    @pytest.mark.usefixtures("_mock_wecom_client")
    def test_test_connection_success(self, wecom_ds_cfg, logger):
        """测试连接成功的情况"""
        plugin = WeComDataSourcePlugin(wecom_ds_cfg, logger)
        result = plugin.test_connection()

        assert not result.error_message
        assert result.user
        assert result.department
        assert result.extras
