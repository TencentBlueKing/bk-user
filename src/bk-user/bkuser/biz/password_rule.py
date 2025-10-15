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

from bkuser.apps.data_source.models import DataSource, DataSourceTypeEnum
from bkuser.common.passwd import PasswordRule
from bkuser.plugins.base import get_default_plugin_cfg
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig


class PasswordRuleHandler:
    @staticmethod
    def get_default_password_rule() -> PasswordRule:
        cfg: LocalDataSourcePluginConfig = get_default_plugin_cfg(DataSourcePluginEnum.LOCAL)  # type: ignore
        assert cfg.password_rule is not None
        return cfg.password_rule.to_rule()

    @staticmethod
    def get_data_source_password_rule(data_source: DataSource) -> PasswordRule | None:
        # 只有本地数据源支持获取密码规则
        if not data_source.is_local:
            return None

        # 仅支持实体数据源和内建管理数据源
        if data_source.type not in [DataSourceTypeEnum.BUILTIN_MANAGEMENT, DataSourceTypeEnum.REAL]:
            return None

        plugin_config = data_source.get_plugin_cfg()

        assert isinstance(plugin_config, LocalDataSourcePluginConfig)
        assert plugin_config.password_rule is not None

        return plugin_config.password_rule.to_rule()
