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

from django.utils.encoding import force_bytes, force_str
from rest_framework.serializers import CharField, Serializer


class EmptySerializer(Serializer):
    """空"""


def is_base64(value: str) -> bool:
    """判断字符串是否为 base64 编码"""
    try:
        return base64.b64encode(base64.b64decode(value)) == force_bytes(value)
    except Exception:  # pylint: disable=broad-except
        return False


class Base64OrPlainField(CharField):
    """兼容 base64 和纯文本字段"""

    def to_internal_value(self, data) -> str:
        if is_base64(data):
            return force_str(base64.b64decode(data))
        return super().to_internal_value(data)
