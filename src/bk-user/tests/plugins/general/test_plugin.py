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
from unittest import mock

import pytest
from bkuser.plugins.general.models import GeneralDataSourcePluginConfig
from bkuser.plugins.general.plugin import GeneralDataSourcePlugin


@pytest.fixture()
def general_ds_cfg(general_ds_plugin_cfg) -> GeneralDataSourcePluginConfig:
    return GeneralDataSourcePluginConfig(**general_ds_plugin_cfg)


def _mocked_fetch_first_item(url, *args, **kwargs):
    if url.endswith("/simple_users"):
        return {
            "id": "100",
            "username": "sanzhang",
        }

    if url.endswith("/users"):
        return {
            "id": "101",
            "username": "sili",
            "full_name": "李四",
            "email": "1234567892@qq.com",
            "phone": "12345678902",
            "phone_country_code": "86",
            "extras": {
                "gender": "female",
            },
            "leaders": ["100"],
            "departments": ["dept_a"],
        }

    if url.endswith("departments"):
        return {
            "id": "dept_a",
            "name": "部门A",
            "parent": "company",
        }

    return None


class TestGeneralDataSourcePlugin:
    @mock.patch(
        "bkuser.plugins.general.plugin.fetch_all_data",
        return_value=[
            {"id": "company", "name": "总公司", "parent": None},
            {"id": "dept_a", "name": "部门A", "parent": "company"},
            {"id": "center_aa", "name": "中心AA", "parent": "dept_a"},
        ],
    )
    def test_get_departments(self, general_ds_cfg):
        plugin = GeneralDataSourcePlugin(general_ds_cfg)
        assert len(plugin.fetch_departments()) == 3  # noqa: PLR2004

    @mock.patch(
        "bkuser.plugins.general.plugin.fetch_all_data",
        return_value=[
            {
                "id": "100",
                "username": "sanzhang",
                "full_name": "张三",
                "email": "1234567891@qq.com",
                "phone": "12345678901",
                "phone_country_code": "86",
                "extras": {
                    "gender": "male",
                },
                "leaders": [],
                "departments": ["company"],
            },
            {
                "id": "101",
                "username": "sili",
                "full_name": "李四",
                "email": "1234567892@qq.com",
                "phone": "12345678902",
                "phone_country_code": "86",
                "extras": {
                    "gender": "female",
                },
                "leaders": ["100"],
                "departments": ["dept_a"],
            },
            {
                "id": "102",
                "username": "wuwang",
                "full_name": "王五",
                "email": "1234567893@qq.com",
                "phone": "12345678903",
                "phone_country_code": "86",
                "extras": {
                    "gender": "male",
                },
                "leaders": ["100", "101"],
                "departments": ["center_aa"],
            },
        ],
    )
    def test_get_users(self, general_ds_cfg):
        plugin = GeneralDataSourcePlugin(general_ds_cfg)
        assert len(plugin.fetch_users()) == 3  # noqa: PLR2004

    @mock.patch("bkuser.plugins.general.plugin.fetch_first_item", new=_mocked_fetch_first_item)
    def test_test_connection(self, general_ds_cfg):
        result = GeneralDataSourcePlugin(general_ds_cfg).test_connection()
        assert not result.error_message
        assert result.user
        assert result.department
        assert result.extras

    @mock.patch("bkuser.plugins.general.plugin.fetch_first_item", new=_mocked_fetch_first_item)
    def test_test_connection_with_simple_users(self, general_ds_cfg):
        """API 返回的字段不足，无法完全解析"""
        general_ds_cfg.server_config.user_api_path = "/api/v1/simple_users"
        result = GeneralDataSourcePlugin(general_ds_cfg).test_connection()
        assert result.error_message == "解析用户/部门数据失败，请确保 API 返回数据符合协议规范"

    @mock.patch("bkuser.plugins.general.plugin.fetch_first_item", new=_mocked_fetch_first_item)
    def test_test_connection_without_data(self, general_ds_cfg):
        """部门 / 用户 API 返回数据为空 -> 数据源不可用"""
        general_ds_cfg.server_config.user_api_path = "/api/v1/bad_path"
        result = GeneralDataSourcePlugin(general_ds_cfg).test_connection()
        assert result.error_message == "获取到的用户/部门数据为空，请检查数据源 API 服务"
