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
from importlib import import_module

from django.conf import settings


def load_plugins():
    plugin_base_dir = settings.BASE_DIR / "bkuser" / "plugins"
    for name in os.listdir(plugin_base_dir):
        if not os.path.isdir(plugin_base_dir / name):
            continue

        # NOTE: 需要先在各个插件的 __init__.py 文件中调用 register_plugin 注册插件
        import_module(f"bkuser.plugins.{name}")


load_plugins()
