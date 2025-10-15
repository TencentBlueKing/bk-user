# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from typing import Any, Dict, List

DEFAULT_SCRUBBED_FIELDS = [
    "password",
    "secret",
    "passwd",
    "api_key",
    "apikey",
    "bk_token",
    "access_token",
    "auth",
    "credentials",
    "bk_app_secret",
    "cookie",
    "bearer",
]


def scrub_data(data: Dict[str, Any], custom_fields: List[str] | None = None) -> Dict[str, Any]:
    """Scrub the data, mask all sensitive data fields.

    :param data: The data dict to scrub.
    :param custom_fields: Additional fields to scrub along with default fields.
    :return: A new dict, with sensitive data masked as "******".
    """
    if not isinstance(data, dict):
        return data

    scrubbed_fields = DEFAULT_SCRUBBED_FIELDS

    if custom_fields:
        scrubbed_fields.extend(custom_fields)

    def _key_is_sensitive(key: str) -> bool:
        """Check if given key is sensitive."""
        return any(field in key.lower() for field in scrubbed_fields)

    result: Dict[str, Any] = {}

    # Use a stack to avoid recursion
    stack = [(data, result)]
    while stack:
        current_data, current_result = stack.pop()

        for key, value in current_data.items():
            if _key_is_sensitive(key):
                current_result[key] = "******"
                continue

            # Process nested data by push it to the stack
            if isinstance(value, dict):
                new_dict: Dict[str, Any] = {}
                current_result[key] = new_dict
                stack.append((value, new_dict))
            else:
                current_result[key] = value
    return result
