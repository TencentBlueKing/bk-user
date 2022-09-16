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
import base64
import datetime
from typing import List

from django.utils.encoding import force_bytes, force_str
from rest_framework import fields, serializers

# 公共的slz, 可能可以挪到别的地方, 后续再看


class DurationTotalSecondField(fields.Field):
    def to_internal_value(self, value) -> datetime.timedelta:
        if isinstance(value, float):
            value = str(value)
        return fields.parse_duration(value)

    def to_representation(self, value: datetime.timedelta):
        return value.total_seconds()


class StringArrayField(fields.CharField):
    """
    String representation of an array field.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.delimiter = kwargs.get("delimiter", ",")

    def to_internal_value(self, data) -> List[str]:
        # convert string to list
        data = super().to_internal_value(data)
        return [x for x in data.split(self.delimiter) if x]


def is_base64(value: str) -> bool:
    """判断字符串是否为 base64 编码"""
    try:
        return base64.b64encode(base64.b64decode(value)) == force_bytes(value)
    except Exception:  # pylint: disable=broad-except
        return False


class Base64OrPlainField(serializers.CharField):
    """兼容 base64 和纯文本字段"""

    def to_internal_value(self, data) -> str:
        if is_base64(data):
            return force_str(base64.b64decode(data))
        return super().to_internal_value(data)
