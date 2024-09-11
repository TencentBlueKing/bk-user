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

from openpyxl import load_workbook
from openpyxl.workbook import Workbook

from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum
from bkuser.utils.uuid import generate_uuid

# 临时存储数据的过期时间
TemporaryStorageDefaultTimeout = 10 * 60


class TemporaryStorage:
    """数据源同步任务时 redis 临时存储"""

    def __init__(self):
        self.storage = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.TEMPORARY_STORAGE)

    def save(self, data: bytes, timeout: int = TemporaryStorageDefaultTimeout) -> str:
        """
        保存临时数据
        :param data: 二进制数据
        :param timeout: 过期时间
        :return: 临时数据唯一标识
        """
        # 生成临时数据的唯一标识，用于后续查询
        temporary_storage_id = generate_uuid()

        encoded_data = base64.b64encode(data).decode("utf-8")
        self.storage.set(temporary_storage_id, encoded_data, timeout)

        return temporary_storage_id

    def get(self, temporary_storage_id: str) -> bytes:
        """
        获取临时数据
        :param temporary_storage_id: 临时数据唯一标识
        :return: 二进制数据
        """
        encoded_data = self.storage.get(temporary_storage_id)
        if not encoded_data:
            raise ValueError(f"data(id={temporary_storage_id}) not found in temporary storage")

        # 获取成功则删除，无需等待过期
        self.storage.delete(temporary_storage_id)

        return base64.b64decode(encoded_data)

    def save_workbook(self, workbook: Workbook) -> str:
        """[快捷方法] 将 Excel workbook 保存到临时存储中，并返回临时存储的数据唯一标识"""

        # 将 workbook 保存到 内存字节流，便于获取到字节内容
        with io.BytesIO() as buffer:
            workbook.save(buffer)
            data = buffer.getvalue()

        return self.save(data)

    def get_workbook(self, temporary_storage_id: str) -> Workbook:
        """[快捷方法] 从临时存储中获取临时数据并转换为 Excel Workbook"""

        data = self.get(temporary_storage_id)

        return load_workbook(filename=io.BytesIO(data))
