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

import logging

from bkuser.apps.tenant.constants import DEFAULT_TENANT_USER_DISPLAY_NAME_EXPRESSION_CONFIG
from bkuser.apps.tenant.models import DataSource, TenantUserDisplayNameExpressionConfig
from bkuser.common.cache import cached

logger = logging.getLogger(__name__)


# 配置 config 缓存过期时间（默认为 2 分钟）
ConfigCacheTimeout = 120


@cached(timeout=ConfigCacheTimeout)
def get_display_name_config(tenant_id: str, data_source_id: int) -> TenantUserDisplayNameExpressionConfig:
    """获取指定租户的展示名配置"""
    data_source = DataSource.objects.get(id=data_source_id)
    # 如果为本租户用户，则直接使用本租户的配置
    if data_source.owner_tenant_id == tenant_id:
        return TenantUserDisplayNameExpressionConfig.objects.get(tenant_id=tenant_id)
    # 如果为协同租户用户，则使用默认的 display_name 表达式配置
    return TenantUserDisplayNameExpressionConfig(**DEFAULT_TENANT_USER_DISPLAY_NAME_EXPRESSION_CONFIG)


# TODO: 后续支持 display_name 缓存
