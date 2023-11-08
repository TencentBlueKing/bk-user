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
from typing import Any, ClassVar, Dict, List

from pydantic import BaseModel


class PluginMetadata(BaseModel):
    """插件基本信息"""

    id: str
    name: str
    description: str


class BasePluginConfig(BaseModel):
    """插件配置基类"""

    # 注：敏感字段声明有以下规范
    # 字段形式如: auth_config.password，
    # 字段类型为 str 或 (str | None)
    # 字段路径中不支持列表下标，只能是字典 key
    sensitive_fields: ClassVar[List[str]] = []


class RawDataSourceUser(BaseModel):
    """原始数据源用户信息"""

    # 用户唯一标识
    code: str
    # 用户名，邮箱，手机号等个人信息
    properties: Dict[str, str]
    # 直接上级信息（code）
    leaders: List[str]
    # 所属部门信息（code）
    departments: List[str]


class RawDataSourceDepartment(BaseModel):
    """原始数据源部门信息"""

    # 部门唯一标识（如：IEG）
    code: str
    # 部门名称
    name: str
    # 上级部门
    parent: str | None


class TestConnectionResult(BaseModel):
    """连通性测试结果，包含示例数据"""

    # 连通性测试错误信息，空则表示正常
    error_message: str
    # 获取到的首个数据源用户
    user: RawDataSourceUser | None = None
    # 获取到的首个数据源部门
    department: RawDataSourceDepartment | None = None
    # 可能便于排查问题的额外数据
    extras: Dict[str, Any] | None = None
