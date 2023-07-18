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
from typing import List

from django.utils.translation import ugettext_lazy as _

from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.error_codes import error_codes


# pylint: disable=function-name-too-long
def list_conflict_before_revert_category(category: ProfileCategory) -> List[str]:
    """
    在还原目录前，查询display_name和domain冲突
    param category: 即将被还原的目录
    return: 冲突列表
    """
    conflicts: List[str] = []

    if ProfileCategory.objects.filter(enabled=True, display_name=category.display_name).exists():
        conflicts.append(_("目录名称重复"))

    if ProfileCategory.objects.filter(enabled=True, domain=category.domain).exists():
        conflicts.append(_("目录登录域重复"))

    return conflicts


# pylint: disable=function-name-too-long
def check_conflict_before_revert_category(category: ProfileCategory):
    """
    在还原目录前，检查是否存在冲突，主要是检查display_name和domain
    param category: 即将被还原的目录
    return: raise Exception
    """
    conflicts = list_conflict_before_revert_category(category)
    if conflicts:
        raise error_codes.REVERT_CATEGORY_CONFLICT.f(",".join(conflicts), replace=True)
