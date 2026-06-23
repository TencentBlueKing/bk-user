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
from functools import cache
from typing import Dict, List, Tuple

from django.conf import settings

from bkuser.apps.tenant.models import TenantUser
from bkuser.common.constants import BkLanguageEnum


@cache
def get_supported_language_choices() -> List[Tuple[str, str]]:
    choices: Dict[str, str] = {}

    for code, name in BkLanguageEnum.get_choices() + list(settings.EXTRA_LANGUAGES):
        choices.setdefault(code, name)

    return list(choices.items())


@cache
def get_supported_language_codes() -> List[str]:
    return [code for code, _ in get_supported_language_choices()]


def update_tenant_user_language(tenant_user: TenantUser, language_code: str) -> bool:
    if language_code not in get_supported_language_codes():
        return False
    tenant_user.language = language_code
    tenant_user.save(update_fields=["language", "updated_at"])
    return True
