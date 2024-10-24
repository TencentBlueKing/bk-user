# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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
import json
from typing import Any, Dict

import jsonref
from drf_yasg import openapi

from bkuser.idp_plugins.base import get_plugin_cfg_cls, list_plugin_cls
from bkuser.utils.pydantic import gen_openapi_schema


def get_idp_plugin_cfg_openapi_schema_map() -> Dict[str, openapi.Schema]:
    """获取认证插件配置类 JsonSchema 映射表，输出是以openapi schema格式"""
    return {
        f"plugin_config:{plugin_cls.id}": gen_openapi_schema(plugin_cls.config_class)
        for plugin_cls in list_plugin_cls()
    }


def get_idp_plugin_cfg_json_schema(plugin_id: str) -> Dict[str, Any]:
    """获取认证源插件配置类的 JsonSchema, without any jsonRef"""
    json_schema = get_plugin_cfg_cls(plugin_id).model_json_schema()
    # replace json refs
    return jsonref.loads(json.dumps(json_schema))
