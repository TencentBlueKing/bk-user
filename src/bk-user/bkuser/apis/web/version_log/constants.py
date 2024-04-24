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
import re

VERSION_PATTERN = re.compile(r"[vV]\d+\.\d+\.\d+")
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")

FILE_NAME = "change_log.md"
FILE_NAME_EN = "change_log_en.md"

FILE_TEXT_SEP = "---"
