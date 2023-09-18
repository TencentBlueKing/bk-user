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
from typing import List, Type

from pydantic import BaseModel

from bkuser.plugins.models import RawDataSourceDepartment, RawDataSourceUser, TestConnectionResult


class BaseDataSourcePlugin(ABC):
    """数据源插件基类"""

    config_class: Type[BaseModel] | None

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
