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
from typing import Optional

from pydantic import BaseModel

from bkuser.apps.data_source.constants import FieldMappingOperation


class DataSourceUserFieldMapping(BaseModel):
    """数据源用户字段映射"""

    # 数据源原始字段
    source_field: str
    # 映射关系
    mapping_operation: FieldMappingOperation
    # 用户管理用户字段
    target_field: str
    # 表达式内容，仅映射关系为表达式时有效
    expression: Optional[str] = None

    def __str__(self):
        if self.mapping_operation == FieldMappingOperation.DIRECT:
            return f"{self.source_field} --> {self.target_field}"

        return f"{self.source_field} --{self.expression}--> {self.target_field}"
