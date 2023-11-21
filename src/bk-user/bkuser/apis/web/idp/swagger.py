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
from typing import Dict

from drf_yasg import openapi

from bkuser.idp_plugins.base import list_plugin_cls
from bkuser.utils.pydantic import gen_openapi_schema


def get_idp_plugin_cfg_schema_map() -> Dict[str, openapi.Schema]:
    """获取认证插件配置类 JsonSchema 映射表"""
    return {
        f"plugin_config:{plugin_cls.id}": gen_openapi_schema(plugin_cls.config_class)
        for plugin_cls in list_plugin_cls()
    }
