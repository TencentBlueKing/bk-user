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
from aenum import Enum
from django.utils.translation import ugettext_lazy as _


class RoleCodeEnum(Enum):
    STAFF = 0
    SUPERUSER = 1
    DEVELOPER = 2
    OPERATOR = 3
    AUDITOR = 4

    _choices_labels = (
        (STAFF, _("普通用户")),
        (SUPERUSER, _("超级管理员")),
        (DEVELOPER, _("开发者")),
        (OPERATOR, _("职能化用户")),
        (AUDITOR, _("审计员")),
    )
