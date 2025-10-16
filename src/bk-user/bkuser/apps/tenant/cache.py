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
from dataclasses import dataclass
from typing import Dict, List, Tuple

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.tenant.constants import DEFAULT_TENANT_USER_DISPLAY_NAME_EXPRESSION_CONFIG
from bkuser.apps.tenant.models import TenantUser, TenantUserDisplayNameExpressionConfig
from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum, cached

logger = logging.getLogger(__name__)

# DisplayName 缓存过期时间（默认为 30 天）
DisplayNameDefaultTimeout = 30 * 24 * 60 * 60
# 配置 config 缓存过期时间（默认为 2 分钟）
ConfigCacheTimeout = 120


def build_default_display_name_config() -> TenantUserDisplayNameExpressionConfig:
    return TenantUserDisplayNameExpressionConfig(**DEFAULT_TENANT_USER_DISPLAY_NAME_EXPRESSION_CONFIG)


@dataclass
class DisplayNameConfigInfo:
    config: TenantUserDisplayNameExpressionConfig
    is_default: bool = False


@cached(timeout=ConfigCacheTimeout)
def get_display_name_config_info(tenant_id: str, data_source_id: int | None = None) -> DisplayNameConfigInfo:
    """获取指定租户的展示名配置信息"""
    if not data_source_id:
        return DisplayNameConfigInfo(
            config=TenantUserDisplayNameExpressionConfig.objects.get(tenant_id=tenant_id),
        )

    data_source = DataSource.objects.get(id=data_source_id)
    # 如果为本租户实名用户，则直接使用本租户的 display_name 表达式配置
    if data_source.owner_tenant_id == tenant_id and data_source.type == DataSourceTypeEnum.REAL:
        return DisplayNameConfigInfo(
            config=TenantUserDisplayNameExpressionConfig.objects.get(tenant_id=tenant_id),
        )

    # 如果为协同租户用户或本租户虚拟用户，则使用默认的 display_name 表达式配置
    return DisplayNameConfigInfo(
        config=build_default_display_name_config(),
        is_default=True,
    )


class DisplayNameCache:
    """租户用户 DisplayName 缓存"""

    def __init__(self):
        self.cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.DISPLAY_NAME)

    def get(self, user_id: str, version: int) -> str | None:
        """获取单个用户的展示名缓存"""

        cache_key = f"{user_id}:{version}"
        return self.cache.get(cache_key)

    def batch_get(self, user_ids: List[str], version: int) -> Dict[str, str]:
        """批量获取用户展示名缓存"""
        if not user_ids:
            return {}

        cache_keys = [f"{user_id}:{version}" for user_id in user_ids]
        cache_data = self.cache.get_many(cache_keys)
        return {cache_key.split(":")[0]: value for cache_key, value in cache_data.items()}

    def set(self, user_id: str, version: int, display_name: str):
        """设置用户的展示名缓存"""
        cache_key = f"{user_id}:{version}"
        self.cache.set(cache_key, display_name, timeout=DisplayNameDefaultTimeout)

    def batch_set(self, display_name_map: Dict[str, str], version: int):
        """批量设置用户展示名缓存"""
        if not display_name_map:
            return

        cache_data = {f"{user_id}:{version}": display_name for user_id, display_name in display_name_map.items()}
        self.cache.set_many(cache_data, timeout=DisplayNameDefaultTimeout)

    def delete(self, user_id: str, version: int):
        """删除单个用户的展示名缓存"""

        cache_key = f"{user_id}:{version}"
        self.cache.delete(cache_key)

    def batch_delete(self, user_ids: List[str], version: int):
        """批量删除用户展示名缓存"""
        if not user_ids:
            return

        cache_keys = [f"{user_id}:{version}" for user_id in user_ids]
        self.cache.delete_many(cache_keys)


class DisplayNameCacheHandler:
    """租户用户 DisplayName 缓存处理器"""

    def __init__(self):
        self.cache = DisplayNameCache()

    def get(self, user: TenantUser) -> str | None:
        """从缓存获取单个本租户实名用户的展示名"""
        config = get_display_name_config_info(user.tenant_id).config
        return self.cache.get(user.id, config.version)

    def set(self, user: TenantUser, display_name: str):
        """缓存单个本租户实名用户的展示名"""
        config = get_display_name_config_info(user.tenant_id).config
        self.cache.set(user.id, config.version, display_name)

    def batch_get(self, users: List[TenantUser]) -> Tuple[Dict[str, str], List[TenantUser]]:
        """从缓存获取本租户实名用户的展示名"""
        if not users:
            return {}, []

        config = get_display_name_config_info(users[0].tenant_id).config
        user_ids = [user.id for user in users]

        # 批量查询缓存
        hit_data = self.cache.batch_get(user_ids, config.version)

        # 找出未命中的用户
        miss_user_ids = set(user_ids) - set(hit_data.keys())
        miss_users = [user for user in users if user.id in miss_user_ids]

        return hit_data, miss_users

    def batch_set(self, users: List[TenantUser], display_name_map: Dict[str, str]):
        """缓存本租户实名用户的展示名"""
        if not users or not display_name_map:
            return

        config = get_display_name_config_info(users[0].tenant_id).config
        self.cache.batch_set(display_name_map, config.version)

    def delete(self, user: TenantUser):
        """删除单个租户用户 DisplayName 缓存"""
        config = get_display_name_config_info(user.tenant_id).config
        self.cache.delete(user.id, config.version)

    def batch_delete(self, users: List[TenantUser]):
        """批量删除租户用户 DisplayName 缓存"""

        if not users:
            return

        config = get_display_name_config_info(users[0].tenant_id).config
        user_ids = [user.id for user in users]
        self.cache.batch_delete(user_ids, config.version)
