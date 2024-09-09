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
from io import BytesIO

from openpyxl import load_workbook
from openpyxl.workbook import Workbook

from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum


class TemporaryStorage:
    """数据源同步任务时 redis 临时存储"""

    def __init__(self, scene: CacheKeyPrefixEnum):
        self.storage = Cache(CacheEnum.REDIS, scene)

    def save_workbook(self, data: Workbook, identifier_key: str, timeout: int) -> None:
        """保存 Workbook 数据至 redis"""
        with io.BytesIO() as buffer:
            data.save(buffer)
            content = buffer.getvalue()

        encoded_data = base64.b64encode(content).decode("utf-8")
        self.storage.set(identifier_key, encoded_data, 2 * timeout)

    def get_workbook(self, identifier_key: str) -> Workbook:
        """从 redis 中获取 Workbook 数据"""
        encoded_data = self.storage.get(identifier_key)
        if not encoded_data:
            raise ValueError("data not found in cache")

        self.storage.delete(identifier_key)
        return load_workbook(filename=BytesIO(base64.b64decode(encoded_data)))
