# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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
from bkuser.apps.data_source.name import gen_data_source_name

PLUGIN_NAME = "本地数据源"


class TestGenDataSourceName:
    """快捷生成数据源名称"""

    @pytest.mark.parametrize(
        ("ds_type", "expected"),
        [
            (DataSourceTypeEnum.REAL, PLUGIN_NAME),
            (DataSourceTypeEnum.VIRTUAL, DataSourceTypeEnum.VIRTUAL),
            (DataSourceTypeEnum.BUILTIN_MANAGEMENT, DataSourceTypeEnum.BUILTIN_MANAGEMENT),
            # 迁移历史模型 / ORM CharField 上 type 是 str
            ("real", PLUGIN_NAME),
            ("virtual", DataSourceTypeEnum.VIRTUAL),
            ("builtin_management", DataSourceTypeEnum.BUILTIN_MANAGEMENT),
        ],
    )
    def test_gen_name(self, ds_type, expected):
        assert gen_data_source_name(ds_type, PLUGIN_NAME) == expected

    def test_real_does_not_deduplicate(self):
        """实名不做冲突检测，相同 plugin_name 会得到相同结果"""
        assert gen_data_source_name(DataSourceTypeEnum.REAL, PLUGIN_NAME) == PLUGIN_NAME
        assert gen_data_source_name(DataSourceTypeEnum.REAL, PLUGIN_NAME) == PLUGIN_NAME
