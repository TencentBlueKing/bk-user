# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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
from typing import Dict, List, Tuple

from django.conf import settings

from bkuser.common.constants import BkLanguageEnum


def get_language_choices() -> List[Tuple[str, str]]:
    choices: Dict[str, str] = {}

    # Q: 这里为什么要使用 BkLanguageEnum 而不是直接使用 settings.LANGUAGES
    # A: settings.LANGUAGES 中的语言代码遵循 Django 规范（如 en-us），
    #    而 BkLanguageEnum 中的语言代码遵循蓝鲸体系规范（如 en），用户管理作为蓝鲸体系的基础服务，
    #    对外提供的语言选项需要使用蓝鲸统一的语言代码，因此基础语言从 BkLanguageEnum 获取，
    #    再拼接 EXTRA_LANGUAGES作为最终的可选语言列表。
    for code, name in BkLanguageEnum.get_choices() + list(settings.EXTRA_LANGUAGES):
        choices.setdefault(code, name)

    return list(choices.items())


def get_language_codes() -> List[str]:
    return [code for code, _ in get_language_choices()]
