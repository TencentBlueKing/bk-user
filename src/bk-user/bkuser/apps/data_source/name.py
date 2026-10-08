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
from bkuser.apps.data_source.constants import DataSourceTypeEnum


def gen_data_source_name(type: DataSourceTypeEnum, plugin_name: str = "") -> str:
    """这里是为了快捷生成数据源名称，特别是内置、虚拟数据源，对于实名，不做冲突检测，由调用方解决"""
    return plugin_name if type == DataSourceTypeEnum.REAL else type


def gen_virtual_data_source_name() -> str:
    return gen_data_source_name(DataSourceTypeEnum.VIRTUAL)


def gen_builtin_management_data_source_name() -> str:
    return gen_data_source_name(DataSourceTypeEnum.BUILTIN_MANAGEMENT)
