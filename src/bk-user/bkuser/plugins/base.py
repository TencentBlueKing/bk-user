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
from abc import ABC, abstractmethod
from typing import Dict, List, Type

from drf_yasg import openapi
from pydantic import BaseModel

from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.models import RawDataSourceDepartment, RawDataSourceUser, TestConnectionResult
from bkuser.utils.pydantic import gen_openapi_schema


class BaseDataSourcePlugin(ABC):
    """数据源插件基类"""

    config_class: Type[BaseModel] | None

    @abstractmethod
    def __init__(self, *args, **kwargs):
        ...

    @abstractmethod
    def fetch_departments(self) -> List[RawDataSourceDepartment]:
        """获取部门信息"""
        ...

    @abstractmethod
    def fetch_users(self) -> List[RawDataSourceUser]:
        """获取用户信息"""
        ...

    @abstractmethod
    def test_connection(self) -> TestConnectionResult:
        """连通性测试（非本地数据源需提供）"""
        ...


_plugin_cls_map: Dict[str | DataSourcePluginEnum, Type[BaseDataSourcePlugin]] = {}


def register_plugin(plugin_id: str | DataSourcePluginEnum, plugin_cls: Type[BaseDataSourcePlugin]):
    """注册插件"""
    _plugin_cls_map[plugin_id] = plugin_cls


def get_plugin_cls(plugin_id: str | DataSourcePluginEnum) -> Type[BaseDataSourcePlugin]:
    """获取指定插件类"""
    if plugin_id not in _plugin_cls_map:
        raise NotImplementedError(f"plugin {plugin_id} not implement or register")

    return _plugin_cls_map[plugin_id]


def get_plugin_cfg_cls(plugin_id: str | DataSourcePluginEnum) -> Type[BaseModel] | None:
    """获取指定插件的配置类"""
    return get_plugin_cls(plugin_id).config_class


def get_plugin_cfg_schema_map() -> Dict[str, openapi.Schema]:
    """获取插件配置类 JsonSchema 映射表"""
    return {
        f"plugin_config:{plugin_id}": gen_openapi_schema(model.config_class)
        for plugin_id, model in _plugin_cls_map.items()
        if model.config_class is not None
    }
