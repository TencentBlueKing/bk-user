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
import json
import random
import string
from typing import Any, Dict

from django.utils.translation import gettext_lazy as _

from .exceptions import ParseRequestBodyError


def parse_request_body_json(body: bytes) -> Dict[str, Any]:
    """解析请求Body Json数据"""
    try:
        request_body = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as error:
        raise ParseRequestBodyError(_("解析异常，Body参数非Json格式数据, {}").format(error))

    return request_body


def generate_random_str(length: int = 8, allowed_chars: str = "") -> str:
    """
    生成指定长度的随机字符串
    :param length: 指定的长度，默认8位
    :param allowed_chars: 随机串里允许出现字符，默认是a-zA-Z0-9
    """
    if not allowed_chars:
        # a-zA-Z0-9
        allowed_chars = string.ascii_letters + string.digits

    return "".join([random.choice(allowed_chars) for _ in range(length)])
