# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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

import os
from typing import Dict, List

from django.conf import settings
from django.utils import translation

from bkuser.common.constants import BkLanguageEnum

from .constants import DATE_PATTERN, FILE_NAME, FILE_NAME_EN, FILE_TEXT_SEP, VERSION_PATTERN


def _read_file_content(file_path: str) -> str:
    """读取文件内容"""
    content = ""
    if os.path.isfile(file_path):
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    return content


def _get_change_log_file_name() -> str:
    """获取日志文件名称"""

    # 检查语言名前缀是否与 BkLanguageEnum.EN 匹配，如 en-us 则视为与 en 匹配
    if translation.get_language().startswith(BkLanguageEnum.EN):
        return FILE_NAME_EN
    return FILE_NAME


def list_version_log() -> List[Dict[str, str]]:
    """
    获取日志版本列表
    :return {版本号, 日期, 文件内容} 字段列表，列表根据版本号从大到小排列
    """
    file_dir = settings.VERSION_LOG_FILES_DIR
    if not os.path.isdir(file_dir):
        return []

    file_name = _get_change_log_file_name()
    if not os.path.isfile(os.path.join(file_dir, file_name)):
        return []

    text = _read_file_content(os.path.join(file_dir, file_name))

    data = []
    for log in text.split(FILE_TEXT_SEP):
        try:
            parts = log.strip().split("\n")

            # 从第一行提取日期
            date = DATE_PATTERN.findall(parts[0])[0]
            # 从第二行提取版本号
            version = VERSION_PATTERN.findall(parts[1])[0]
            # 剩下即为版本日志内容
            content = "\n".join(parts[1:])  # 去除日期注释, 重新组合

            data.append({"version": version, "date": date, "content": content})
        except Exception:  # noqa: PERF203
            pass

    return data
