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
import datetime

from blue_krill.data_types.enum import EnumField, StructuredEnum


class BkLanguageEnum(str, StructuredEnum):
    ZH_CN = EnumField("zh-cn", label="中文")
    EN = EnumField("en", label="英文")


# 永久：2100-01-01 00:00:00
PERMANENT_TIME = datetime.datetime(year=2100, month=1, day=1, hour=0, minute=0, second=0)

# 敏感信息掩码（7 位 * 是故意的，避免遇到用户输入 6/8 位 * 的情况）
SENSITIVE_MASK = "*******"
