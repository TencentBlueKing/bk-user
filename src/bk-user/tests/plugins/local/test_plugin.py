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
from bkuser.plugins.local.models import LocalDataSourcePluginConfig
from bkuser.plugins.local.plugin import LocalDataSourcePlugin


@pytest.fixture
def local_ds_cfg(local_ds_plugin_cfg):
    return LocalDataSourcePluginConfig(**local_ds_plugin_cfg)


class TestLocalDataSourcePlugin:
    def test_get_departments(self, local_ds_cfg, logger, user_workbook):
        plugin = LocalDataSourcePlugin(local_ds_cfg, logger, user_workbook)
        assert len(plugin.fetch_departments()) == 12  # noqa: PLR2004

    def test_get_users(self, local_ds_cfg, logger, user_workbook):
        plugin = LocalDataSourcePlugin(local_ds_cfg, logger, user_workbook)
        assert len(plugin.fetch_users()) == 12  # noqa: PLR2004

    def test_test_connection(self, local_ds_cfg, logger, user_workbook):
        with pytest.raises(NotImplementedError):
            LocalDataSourcePlugin(local_ds_cfg, logger, user_workbook).test_connection()
