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
import string
from typing import Dict


class TwoBraceTemplate(string.Template):
    """A template class similar to `string.Template`, but use `{{` and `}}` as delimiters.

    This class supports Django-style template variables: `{{ variable }}`.

    - Use '{{{{' to escape a double brace
    - Only '{{' need to be escaped, '}}' is treated as a normal character
    """

    # Override the delimiter property because `string.Template` uses it
    delimiter = "{{"

    delim = delimiter
    # The identifier is copied from `string.Template`
    id = r"(?a:[_a-z][_a-z0-9]*)"

    # "named" and "braced" patterns are modified
    pattern = rf"""
        {delim}(?:
            (?P<escaped>{delim})        |   # Escape sequence of two delimiters
            \s*(?P<named>{id})\s*\}}\}} |   # delimiter, optional spaces, identifier, optional spaces, closing braces
            (?P<braced>\b\B)            |   # delimiter and a braced identifier, **modified to never match anything**
            (?P<invalid>)               |   # Other ill-formed delimiter exprs
        )
        """  # type: ignore


def basic_str_format(template: str, context: Dict[str, str]) -> str:
    """Safely substitute Django-style template variables, only support basic string substitution,
    features such as attribute access and slicing are not supported.

    It's recommended to use this function when the template is untrusted.

    :param template: The template string.
    :param context: The context dictionary.
    :return: The formatted string.
    """
    return TwoBraceTemplate(template).substitute(**context)
