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
from typing import Any

from pydantic import create_model

from .constants import GlobalSettingEnum

# 定义每个配置的value类型，支持Python默认类型和Pydantic声明的数据类型
global_setting_value_type_map = {
    GlobalSettingEnum.TENANT_VISIBLE: bool,
}


def validate_global_setting_value_type(global_setting_id: GlobalSettingEnum, value) -> Any:
    """校验并返回value类型"""
    if global_setting_id not in global_setting_value_type_map:
        raise ValueError(f"global setting {global_setting_id} not define value type")

    # 动态创建value数据类
    dynamic_value_model = create_model(
        "DynamicValueModel", value=(global_setting_value_type_map[global_setting_id], ...)
    )

    data = dynamic_value_model(value=value)

    return data.model_dump(include={"value"})["value"]
