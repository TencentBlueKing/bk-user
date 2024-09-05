# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import base64
import io
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, Dict

from openpyxl import load_workbook
from openpyxl.workbook import Workbook

from bkuser.common.cache import Cache


class TemporaryStorageBackend(ABC):
    """临时存储基类"""

    @abstractmethod
    def save(self, workbook: Workbook, data: Dict[str, Any]) -> None:
        """保存 Workbook 数据"""

    @abstractmethod
    def get(self, data: Dict[str, Any]) -> Workbook:
        """获取 Workbook 数据"""


class RedisTemporaryStorage(TemporaryStorageBackend):
    """redis 临时存储"""

    def __init__(self, cache: Cache):
        self.cache = cache

    def save(self, workbook: Workbook, data: Dict[str, Any]) -> None:
        """保存 Workbook 数据至 redis"""
        with io.BytesIO() as buffer:
            workbook.save(buffer)
            content = buffer.getvalue()

        encoded_data = base64.b64encode(content).decode("utf-8")
        self.cache.set(data["key"], encoded_data, 2 * data["timeout"])

    def get(self, data: Dict[str, Any]) -> Workbook:
        """从 redis 中获取 Workbook 数据"""
        key = data["key"]
        encoded_data = self.cache.get(key)
        self.cache.delete(key)

        return load_workbook(filename=BytesIO(base64.b64decode(encoded_data)))
