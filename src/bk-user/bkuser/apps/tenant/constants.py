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
from enum import Enum

import pytz


class LanguageEnum(Enum):
    ZH_CN = "zh-cn"
    EN = "en"

    _choices_labels = ((ZH_CN, "中文"), (EN, "英文"))

    @classmethod
    def get_choices(cls) -> tuple:
        return cls._choices_labels.value


TIME_ZONE_LIST = pytz.common_timezones
TIME_ZONE_CHOICES = [(i, i) for i in TIME_ZONE_LIST]
