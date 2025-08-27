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
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.biz.password_rule import PasswordRuleHandler
from bkuser.common.passwd import PasswordRule
from bkuser.plugins.base import get_default_plugin_cfg
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

pytestmark = pytest.mark.django_db


class TestPasswordRuleHandler:
    """测试密码规则服务类"""

    def test_get_default_password_rule(self):
        """测试获取默认密码规则"""
        password_rule = PasswordRuleHandler.get_default_password_rule()

        assert isinstance(password_rule, PasswordRule)
        assert password_rule.min_length == 12
        assert password_rule.max_length == 32
        assert password_rule.contain_lowercase is True
        assert password_rule.contain_uppercase is True
        assert password_rule.contain_digit is True
        assert password_rule.contain_punctuation is True

    def test_get_data_source_password_rule_success(self, full_local_data_source):
        """测试成功获取数据源密码规则"""
        password_rule = PasswordRuleHandler.get_data_source_password_rule(full_local_data_source)

        assert isinstance(password_rule, PasswordRule)
        assert password_rule.min_length == 12
        assert password_rule.contain_lowercase is True

    def test_get_data_source_password_rule_not_local(self, random_tenant):
        """测试非本地数据源失败"""
        # 创建虚拟数据源
        cfg: LocalDataSourcePluginConfig = get_default_plugin_cfg(DataSourcePluginEnum.LOCAL)  # type: ignore
        data_source = DataSource.objects.create(
            owner_tenant_id=random_tenant.id,
            plugin_id=DataSourcePluginEnum.LOCAL,
            type=DataSourceTypeEnum.VIRTUAL,
            plugin_config=cfg,
        )

        result = PasswordRuleHandler.get_data_source_password_rule(data_source)
        assert result is None

    def test_get_data_source_password_rule_disabled(self, random_tenant):
        """测试未启用密码的数据源失败"""
        cfg: LocalDataSourcePluginConfig = get_default_plugin_cfg(DataSourcePluginEnum.LOCAL)  # type: ignore
        cfg.enable_password = False
        data_source = DataSource.objects.create(
            owner_tenant_id=random_tenant.id,
            plugin_id=DataSourcePluginEnum.LOCAL,
            type=DataSourceTypeEnum.REAL,
            plugin_config=cfg,
        )

        result = PasswordRuleHandler.get_data_source_password_rule(data_source)
        assert result is None
