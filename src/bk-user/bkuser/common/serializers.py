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
from typing import List

from rest_framework import fields


class StringArrayField(fields.CharField):
    """String representation of an array field"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.delimiter = kwargs.get("delimiter", ",")

    def to_internal_value(self, data) -> List[str]:
        # convert string to list
        data = super().to_internal_value(data)
        return [x.strip() for x in data.split(self.delimiter) if x]
