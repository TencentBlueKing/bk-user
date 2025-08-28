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

import re

from pypinyin import Style, pinyin

# 中文汉字正则表达式
CHINESE_NAME_PATTERN = re.compile(r"[\u4e00-\u9fff·]+")


def is_chinese_name(full_name: str) -> bool:
    """判断是否为中文姓名"""
    return bool(CHINESE_NAME_PATTERN.fullmatch(full_name))


def generate_chinese_name_initial(full_name: str) -> str:
    """生成中文姓名首字母缩写"""
    if not is_chinese_name(full_name):
        return ""

    initials = [p[0] for p in pinyin(full_name, style=Style.FIRST_LETTER, strict=False)]
    return "".join(initials).lower()
