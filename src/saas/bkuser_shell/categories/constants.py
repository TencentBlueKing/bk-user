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

from django.utils.translation import ugettext_lazy as _


class CategoryTypeEnum(Enum):
    LOCAL = "local"
    MAD = "mad"
    LDAP = "ldap"
    CUSTOM = "custom"
    # 特殊的类型，仅在未解耦前桥接
    PLUGGABLE = "pluggable"

    _choices_labels = (
        (LOCAL, _("本地目录")),
        (MAD, _("Microsoft Active Directory")),
        (LDAP, _("LDAP")),
        (CUSTOM, _("自定义目录")),
        (PLUGGABLE, "可插拔目录"),
    )
