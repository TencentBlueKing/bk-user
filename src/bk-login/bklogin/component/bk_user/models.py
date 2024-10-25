# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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

from typing import Any, Dict, List

from pydantic import BaseModel

from .constants import IdpStatus


class UniqueEnabledTenantIdp(BaseModel):
    """唯一可用的租户认证源"""

    id: str
    plugin_id: str
    owner_tenant_id: str


class GlobalSetting(BaseModel):
    """全局配置信息"""

    bk_user_url: str
    unique_enabled_tenant_idp: UniqueEnabledTenantIdp | None


class CollaborationTenant(BaseModel):
    """协同租户信息"""

    id: str
    name: str


class TenantInfo(BaseModel):
    """租户信息"""

    id: str
    name: str
    logo: str = ""

    collaboration_tenants: List[CollaborationTenant] = []


class IdpInfo(BaseModel):
    """认证源基本信息"""

    id: str
    name: str
    plugin_id: str
    data_source_type: str


class IdpPluginInfo(BaseModel):
    id: str
    name: str


class IdpDetail(BaseModel):
    """认证源详情"""

    id: str
    name: str
    status: IdpStatus
    plugin: IdpPluginInfo
    owner_tenant_id: str
    plugin_config: Dict[str, Any]


class TenantUserInfo(BaseModel):
    id: str
    username: str
    full_name: str


class TenantUserDetailInfo(TenantUserInfo):
    display_name: str
    tenant_id: str
    language: str
    time_zone: str
