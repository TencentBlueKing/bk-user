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
from pathlib import Path


def load_plugins():
    """加载插件"""
    # 插件目录(即当前目录)
    # Note: 这里不能使用Path(__file__).resolve()，因为resolve后会指向软链接目标目录，而非当前目录的真实目录
    plugin_base_dir = Path(__file__).parent
    # 当前包
    package = f"{plugin_base_dir.parent.name}.{plugin_base_dir.name}"
    # 子目录列表（即各个插件目录名）
    sub_dirs = [name for name in os.listdir(plugin_base_dir) if os.path.isdir(plugin_base_dir / name)]
    # 遍历加载各个插件
    for name in sub_dirs:
        # NOTE: 各个插件需要在插件的 __init__.py 文件中调用 register_plugin 注册插件
        import_module(f".{name}", package)


load_plugins()
