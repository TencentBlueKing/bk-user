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
import os
from pathlib import Path

from .handlers import *  # noqa
from .login import LoginHandler
from .syncer import LDAPSyncer
from bkuser_core.categories.plugins.plugin import DataSourcePlugin

DataSourcePlugin(
    name="ldap",
    syncer_cls=LDAPSyncer,
    login_handler_cls=LoginHandler,
    allow_client_write=False,
    category_type="ldap",
    settings_path=os.path.dirname(__file__) / Path("settings.yaml"),
).register()

# NOTE: 策略-每一次排查, 都简化复杂度, 加相关的日志等, 为未来的排查降低成本
