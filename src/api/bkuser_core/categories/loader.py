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
import logging
from typing import TYPE_CHECKING, Dict

from .constants import CategoryType
from .plugins.constants import PLUGIN_NAME_SETTING_KEY
from bkuser_core.user_settings.loader import ConfigProvider

if TYPE_CHECKING:
    from bkuser_core.categories.models import ProfileCategory  # noqa
    from bkuser_core.categories.plugins.plugin import DataSourcePlugin  # noqa


logger = logging.getLogger(__name__)


class PluginDoesNotExist(Exception):
    """插件不存在异常"""


class PluginAlreadyExisted(Exception):
    """插件已存在异常"""


_global_plugins: Dict[str, "DataSourcePlugin"] = {}


def get_plugin_by_category(category: "ProfileCategory") -> "DataSourcePlugin":
    """通过 category 类型获取插件名"""
    if category.type == CategoryType.PLUGGABLE.value:
        plugin_name = ConfigProvider(category.id)[PLUGIN_NAME_SETTING_KEY]
        return get_plugin_by_name(plugin_name)

    for n, p in _global_plugins.items():
        if p.category_type == category.type:
            return p
    raise ValueError(f"Plugin with category type: {category.type} does not exist")


def get_plugin_by_name(name: str) -> "DataSourcePlugin":
    try:
        return _global_plugins[name]
    except KeyError:
        raise PluginDoesNotExist(f"Plugin with name: {name} does not exist")


def register_plugin(plugin: "DataSourcePlugin"):
    try:
        if get_plugin_by_name(plugin.name):
            logger.warning(f"Plugin with name: {plugin.name} already existed")
    except PluginDoesNotExist:
        _global_plugins[plugin.name] = plugin
        logger.info("➕Plugin[%s] loaded.", plugin.name)
