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
from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.utils.translation import gettext_lazy as _


class ZxcvbnPattern(str, StructuredEnum):
    """密码片段匹配模式"""

    REPEAT = EnumField("repeat", label=_("重复"))
    DATE = EnumField("date", label=_("日期"))
    DICTIONARY = EnumField("dictionary", label=_("字典"))
    SEQUENCE = EnumField("sequence", label=_("序列"))
    REGEX = EnumField("regex", label=_("正则"))
    SPATIAL = EnumField("spatial", label=_("空间连续性"))
    BRUTEFORCE = EnumField("bruteforce", label=_("暴力破解"))
