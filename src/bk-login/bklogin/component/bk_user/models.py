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
from typing import Any, Dict, List

from pydantic import BaseModel

from .constants import IdpStatus


class EnabledIdp(BaseModel):
    id: str
    plugin_id: str


class OnlyEnabledAuthTenant(BaseModel):
    id: str
    name: str
    logo: str = ""
    enabled_idps: List[EnabledIdp]


class GlobalInfo(BaseModel):
    """全局信息"""

    tenant_visible: bool
    enabled_auth_tenant_number: int
    # 当且仅当只有一个租户认证可用时候才有值，即 enabled_auth_tenant_number = 1 时才有值
    only_enabled_auth_tenant: OnlyEnabledAuthTenant | None


class TenantInfo(BaseModel):
    """租户信息"""

    id: str
    name: str
    logo: str = ""


class IdpPluginInfo(BaseModel):
    id: str
    name: str


class IdpInfo(BaseModel):
    """认证源基本信息"""

    id: str
    name: str
    status: IdpStatus
    plugin: IdpPluginInfo


class IdpDetailInfo(IdpInfo):
    """认证源详情"""

    owner_tenant_id: str
    plugin_config: Dict[str, Any]


class TenantUserInfo(BaseModel):
    id: str
    username: str
    full_name: str
    display_name: str


class TenantUserDetailInfo(TenantUserInfo):
    tenant_id: str
    language: str
    time_zone: str
