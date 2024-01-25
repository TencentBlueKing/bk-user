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


class IdpCategory(str, StructuredEnum):
    """认证源分类"""

    ENTERPRISE = EnumField("enterprise", label=_("企业"))
    SOCIAL = EnumField("social", label=_("社交"))


class IdpStatus(str, StructuredEnum):
    """认证源状态"""

    ENABLED = EnumField("enabled", label=_("启用"))
    DISABLED = EnumField("disabled", label=_("未启用"))


class AllowBindScopeObjectType(str, StructuredEnum):
    """社会化认证源，允许绑定的范围对象类型"""

    USER = EnumField("user", label=_("用户"))
    DEPARTMENT = EnumField("department", label=_("部门"))
    DATA_SOURCE = EnumField("data_source", label=_("数据源"))
    TENANT = EnumField("tenant", label=_("租户"))
    ANY = EnumField("*", label=_("任意"))


# 社会化认证源，允许绑定的范围为任意对象ID
ANY_ALLOW_BIND_SCOPE_OBJECT_ID = "*"
