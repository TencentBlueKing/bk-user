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
from collections import defaultdict
from typing import Dict, List, Tuple

from bkuser.apps.tenant.models import TenantUser, TenantUserDisplayNameExpressionConfig
from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum

logger = logging.getLogger(__name__)

# DisplayName 缓存过期时间（默认为 30 天）
DisplayNameDefaultTimeout = 30 * 24 * 60 * 60


class DisplayNameCacheManager:
    """租户用户 DisplayName 缓存管理器"""

    cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.DISPLAY_NAME)

    @classmethod
    def get_display_name(cls, user_id: str, version: int) -> str | None:
        """获取单个用户的展示名缓存"""

        cache_key = f"{user_id}:{version}"
        return cls.cache.get(cache_key)

    @classmethod
    def batch_get_display_name(cls, user_ids: List[str], version: int) -> Dict[str, str]:
        """批量获取用户展示名缓存"""
        if not user_ids:
            return {}

        cache_keys = [f"{user_id}:{version}" for user_id in user_ids]
        cache_mappings = cls.cache.get_many(cache_keys)
        return {cache_key.split(":")[0]: value for cache_key, value in cache_mappings.items()}

    @classmethod
    def set_display_name(cls, user_id: str, version: int, display_name: str):
        """设置用户的展示名缓存"""
        cache_key = f"{user_id}:{version}"
        cls.cache.set(cache_key, display_name, timeout=DisplayNameDefaultTimeout)

    @classmethod
    def batch_set_display_name(cls, display_name_map: Dict[str, str], version: int):
        """批量设置用户展示名缓存"""
        if not display_name_map:
            return

        cache_mappings = {f"{user_id}:{version}": display_name for user_id, display_name in display_name_map.items()}
        cls.cache.set_many(cache_mappings, timeout=DisplayNameDefaultTimeout)

    @classmethod
    def delete_display_name(cls, user_id: str, version: int) -> None:
        """删除单个用户的展示名缓存"""

        cache_key = f"{user_id}:{version}"
        cls.cache.delete(cache_key)

    @classmethod
    def batch_delete_display_name(cls, user_ids: List[str], version: int):
        """批量删除用户展示名缓存"""
        if not user_ids:
            return

        for user_id in user_ids:
            cls.delete_display_name(user_id, version)


class DisplayNameCacheHandler:
    """DisplayName 缓存处理类"""

    @staticmethod
    def get_display_names_from_cache(
        users: List[TenantUser],
        data_source_config_map: Dict[int, TenantUserDisplayNameExpressionConfig],
    ) -> Tuple[Dict[str, str], List[TenantUser]]:
        """从缓存获取已有的 display_name，返回缓存结果和需要渲染的用户列表"""
        display_name_map: Dict[str, str] = {}
        users_need_render: List[TenantUser] = []

        # 按 data_source_id 分组用户，每组使用相同的 config
        data_source_user_map: Dict[int, List[TenantUser]] = defaultdict(list)
        for user in users:
            data_source_user_map[user.data_source_id].append(user)

        for data_source_id, tenant_users in data_source_user_map.items():
            config = data_source_config_map[data_source_id]

            # 尝试从缓存获取这组用户的 display_name
            user_ids = [user.id for user in tenant_users]
            cached_display_names = DisplayNameCacheManager.batch_get_display_name(user_ids, config.version)
            display_name_map.update(cached_display_names)

            # 将缓存中没有的用户加入待渲染列表
            cached_user_ids = set(cached_display_names.keys())
            users_need_render.extend([user for user in tenant_users if user.id not in cached_user_ids])

        return display_name_map, users_need_render

    @staticmethod
    def set_rendered_display_names_cache(
        users_need_render: List[TenantUser],
        data_source_config_map: Dict[int, TenantUserDisplayNameExpressionConfig],
        rendered_display_name_map: Dict[str, str],
    ):
        """将渲染结果缓存"""
        # 因为不同租户的表达式版本号不同，所以需要按 data_source_id 分组进行缓存
        data_source_user_map: Dict[int, List[TenantUser]] = defaultdict(list)
        for user in users_need_render:
            data_source_user_map[user.data_source_id].append(user)

        for data_source_id, tenant_users in data_source_user_map.items():
            config = data_source_config_map[data_source_id]
            display_name_map = {user.id: rendered_display_name_map[user.id] for user in tenant_users}
            # 缓存渲染结果
            DisplayNameCacheManager.batch_set_display_name(display_name_map, config.version)

    @staticmethod
    def delete_display_name_cache(user: TenantUser):
        """失效 DisplayName 缓存"""
        data_source_user = user.data_source_user
        users = TenantUser.objects.filter(data_source_user=data_source_user)

        config = TenantUserDisplayNameExpressionConfig.objects.get(tenant_id=user.data_source.owner_tenant_id)
        DisplayNameCacheManager.batch_delete_display_name([user.id for user in users], config.version)

    @staticmethod
    def batch_delete_display_name_cache(users: List[TenantUser]):
        """批量失效 DisplayName 缓存"""
        if not users:
            return

        # 失效的用户都属于同一数据源，且表达式配置相同
        config = TenantUserDisplayNameExpressionConfig.objects.get(tenant_id=users[0].data_source.owner_tenant_id)
        DisplayNameCacheManager.batch_delete_display_name([user.id for user in users], config.version)
