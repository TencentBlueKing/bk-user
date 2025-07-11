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
import string
from typing import Dict


class BraceOnlyTemplate(string.Template):
    """A template class similar to `string.Template`, but use `{` as the delimiter and
    only supports single-braces formatted variables: `{<name>}`.

    - Use '{{' to escape a single brace
    - Only '{' need to be escaped, '}' is treated as a normal character
    """

    # Override the delimiter property because `string.Template` uses it
    delimiter = "{"

    delim = delimiter
    # The identifier is copied from `string.Template`
    id = r"(?a:[_a-z][_a-z0-9]*)"

    # "named" and "braced" patterns are modified
    pattern = rf"""
        {delim}(?:
            (?P<escaped>{delim})  |   # Escape sequence of two delimiters
            (?P<named>{id})}}     |   # delimiter and a Python identifier, **modified to ends with a bracket**
            (?P<braced>\b\B)      |   # delimiter and a braced identifier, **modified to never match anything**
            (?P<invalid>)             # Other ill-formed delimiter exprs
        )
        """  # type: ignore


def safe_str_format(template: str, context: Dict[str, str]) -> str:
    """This function is similar to `str.format`, but only support basic string substitution,
    features such as attribute access and slicing are not supported.

    It's recommended to use this function when the template is untrusted.

    :param template: The template string.
    :param context: The context dictionary.
    :return: The formatted string.
    """
    return BraceOnlyTemplate(template).substitute(**context)
