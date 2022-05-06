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
from .handlers import *  # noqa
from .login import LoginHandler
from .syncer import ExcelSyncer
from bkuser_core.categories.plugins.plugin import DataSourcePlugin

# Q: 为什么 local 插件不使用 PluginConfig 注册 SettingMeta ?
# A: 因为目前与 local 插件相关的大部分配置在整个登录流程中都有使用，相当于全局配置，所以暂不放在插件配置中
DataSourcePlugin(
    name="local",
    syncer_cls=ExcelSyncer,
    login_handler_cls=LoginHandler,
    allow_client_write=True,
    category_type="local",
).register()
