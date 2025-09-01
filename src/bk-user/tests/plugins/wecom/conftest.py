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

from unittest import mock

import pytest
from bkuser.plugins.wecom.client import WeComAPIClient
from bkuser.plugins.wecom.models import WeComDataSourcePluginConfig

# 企业微信部门数据
wecom_departments = [
    {
        "id": 1,
        "name": "总公司",
        "name_en": "Company",
        "parentid": 0,
        "order": 1,
    },
    {
        "id": 2,
        "name": "技术部",
        "name_en": "Tech Dept",
        "parentid": 1,
        "order": 2,
    },
    {
        "id": 3,
        "name": "产品部",
        "name_en": "Product Dept",
        "parentid": 1,
        "order": 3,
    },
    {
        "id": 4,
        "name": "前端团队",
        "name_en": "Frontend Team",
        "parentid": 2,
        "order": 1,
    },
    {
        "id": 5,
        "name": "后端团队",
        "name_en": "Backend Team",
        "parentid": 2,
        "order": 2,
    },
]

# 模拟企业微信用户数据
wecom_users = [
    {
        "userid": "zhangsan",
        "name": "张三",
        "department": [1],
        "position": "总经理",
        "is_leader_in_dept": [1],
        "direct_leader": [],
        "telephone": "021-12345678",
        "alias": "zhangsan",
        "main_department": 1,
        "status": 1,
    },
    {
        "userid": "lisi",
        "name": "李四",
        "department": [2, 4],
        "position": "前端工程师",
        "is_leader_in_dept": [0, 1],
        "direct_leader": ["zhangsan"],
        "telephone": "",
        "alias": "lisi",
        "main_department": 4,
        "status": 1,
    },
    {
        "userid": "wangwu",
        "name": "王五",
        "department": [5],
        "position": "后端工程师",
        "is_leader_in_dept": [0],
        "direct_leader": ["zhangsan"],
        "telephone": "010-87654321",
        "alias": "wangwu",
        "main_department": 5,
        "status": 1,
    },
]


@pytest.fixture
def _mock_wecom_client():
    """模拟企业微信客户端"""
    with (
        mock.patch.object(WeComAPIClient, "access_token") as mock_access_token,
        mock.patch.object(WeComAPIClient, "fetch_department_list") as mock_dept_list,
        mock.patch.object(WeComAPIClient, "fetch_department_info") as mock_dept_info,
        mock.patch.object(WeComAPIClient, "fetch_user_info") as mock_user_info,
    ):
        mock_access_token.return_value = "test_access_token"

        # Mock 部门列表
        mock_dept_list.return_value = [1, 2, 3, 4, 5]

        # Mock 部门信息
        def mock_dept_info_func(dept_id: int):
            return next((d for d in wecom_departments if d["id"] == dept_id), {})

        mock_dept_info.side_effect = mock_dept_info_func

        # Mock 用户信息
        def mock_user_info_func(dept_id: int):
            return [u for u in wecom_users if dept_id in u["department"]]  # type: ignore[operator]

        mock_user_info.side_effect = mock_user_info_func

        yield


@pytest.fixture
def wecom_ds_cfg(wecom_ds_plugin_cfg) -> WeComDataSourcePluginConfig:
    """企业微信数据源配置"""
    return WeComDataSourcePluginConfig(**wecom_ds_plugin_cfg)
