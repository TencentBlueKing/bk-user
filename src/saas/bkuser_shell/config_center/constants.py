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
from django.utils.translation import ugettext_lazy as _

from bkuser_shell.common.constants import ChoicesEnum


class DynamicFieldTypeEnum(ChoicesEnum):
    STRING = "string"
    ONE_ENUM = "one_enum"
    MULTI_ENUM = "multi_enum"
    NUMBER = "number"
    TIMER = "timer"

    _choices_labels = (
        (STRING, _("字符串")),
        (ONE_ENUM, _("枚举")),
        (MULTI_ENUM, _("多枚举")),
        (NUMBER, _("数值")),
        (TIMER, _("日期")),
    )
