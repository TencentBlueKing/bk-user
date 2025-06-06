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
from typing import Dict, List, Tuple

from bkuser.apps.data_source.models import DataSource
from bkuser.apps.tenant.constants import DEFAULT_TENANT_USER_DISPLAY_NAME_EXPRESSION_CONFIG
from bkuser.apps.tenant.models import TenantUser, TenantUserDisplayNameExpressionConfig
from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum, cached

logger = logging.getLogger(__name__)

# DisplayName 缓存过期时间（默认为 30 天）
DisplayNameDefaultTimeout = 30 * 24 * 60 * 60
# 配置 config 缓存过期时间（默认为 2 分钟）
ConfigCacheTimeout = 120


@cached(timeout=ConfigCacheTimeout)
def get_display_name_config(tenant_id: str) -> TenantUserDisplayNameExpressionConfig:
    """获取指定租户的展示名配置"""
    return TenantUserDisplayNameExpressionConfig.objects.get(tenant_id=tenant_id)


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
    def delete_display_name(cls, user_id: str, version: int):
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
    def build_default_display_name_config() -> TenantUserDisplayNameExpressionConfig:
        return TenantUserDisplayNameExpressionConfig(**DEFAULT_TENANT_USER_DISPLAY_NAME_EXPRESSION_CONFIG)

    @staticmethod
    def _split_users_by_tenant(users: List[TenantUser]) -> Tuple[List[TenantUser], List[TenantUser]]:
        """区分本租户用户与协同租户用户"""
        if not users:
            return [], []

        # 为了避免 n + 1 问题，需要提前获取所有用户数据源所属租户的信息
        data_source_ids = [user.data_source_id for user in users]
        data_source_tenant_map = dict(
            DataSource.objects.filter(id__in=data_source_ids).values_list("id", "owner_tenant_id")
        )

        current_tenant_users: List[TenantUser] = []
        collaboration_users: List[TenantUser] = []
        for user in users:
            owner_tenant_id = data_source_tenant_map[user.data_source_id]
            if owner_tenant_id == user.tenant_id:
                current_tenant_users.append(user)
            else:
                collaboration_users.append(user)

        return current_tenant_users, collaboration_users

    @staticmethod
    def _get_cached_display_names(
        users: List[TenantUser],
        config: TenantUserDisplayNameExpressionConfig,
    ) -> Tuple[Dict[str, str], List[TenantUser]]:
        if not users:
            return {}, []

        # 批量获取用户的 ID 列表并从缓存获取 display_name
        user_ids = [user.id for user in users]
        cached_display_names = DisplayNameCacheManager.batch_get_display_name(user_ids, config.version)

        # 记录未缓存的用户，后续需要重新渲染
        cached_user_ids = list(cached_display_names.keys())
        users_need_render = [user for user in users if user.id not in cached_user_ids]

        return cached_display_names, users_need_render

    @staticmethod
    def get_display_names_from_cache(
        users: List[TenantUser],
    ) -> Tuple[Dict[str, str], List[TenantUser]]:
        """从缓存获取已有的 display_name，返回缓存结果和需要渲染的用户列表"""
        display_name_map: Dict[str, str] = {}
        users_need_render: List[TenantUser] = []

        # 按租户类型分组用户
        current_tenant_users, collaboration_users = DisplayNameCacheHandler._split_users_by_tenant(users)

        # 批量处理本租户用户
        if current_tenant_users:
            config = get_display_name_config(current_tenant_users[0].tenant_id)
            cached_names, uncached_users = DisplayNameCacheHandler._get_cached_display_names(
                current_tenant_users, config
            )
            display_name_map.update(cached_names)
            users_need_render.extend(uncached_users)

        # 批量处理协同租户用户
        if collaboration_users:
            config = DisplayNameCacheHandler.build_default_display_name_config()
            cached_names, uncached_users = DisplayNameCacheHandler._get_cached_display_names(
                collaboration_users, config
            )
            display_name_map.update(cached_names)
            users_need_render.extend(uncached_users)

        return display_name_map, users_need_render

    @staticmethod
    def set_rendered_display_names_cache(
        users_need_render: List[TenantUser],
        display_name_map: Dict[str, str],
    ):
        """将渲染结果缓存"""
        # 按租户类型分组用户
        current_tenant_users, collaboration_users = DisplayNameCacheHandler._split_users_by_tenant(users_need_render)

        # 批量处理本租户用户缓存
        if current_tenant_users:
            config = get_display_name_config(current_tenant_users[0].tenant_id)
            current_tenant_display_names = {user.id: display_name_map[user.id] for user in current_tenant_users}
            DisplayNameCacheManager.batch_set_display_name(current_tenant_display_names, config.version)

        # 批量处理协同租户用户缓存
        if collaboration_users:
            config = DisplayNameCacheHandler.build_default_display_name_config()
            collaboration_display_names = {user.id: display_name_map[user.id] for user in collaboration_users}
            DisplayNameCacheManager.batch_set_display_name(collaboration_display_names, config.version)

    @staticmethod
    def delete_display_name_cache(user: TenantUser):
        """失效 DisplayName 缓存"""
        # NOTE：这里输入的一定为当前租户用户，因为只有当前租户用户才会触发这个方法
        data_source_user = user.data_source_user
        collaboration_tenant_users = TenantUser.objects.filter(data_source_user=data_source_user).exclude(
            tenant_id=user.tenant_id
        )

        # 删除本租户用户缓存
        config = get_display_name_config(user.tenant_id)
        DisplayNameCacheManager.delete_display_name(user.id, config.version)

        # 删除协同租户用户缓存
        if collaboration_tenant_users:
            config = DisplayNameCacheHandler.build_default_display_name_config()
            DisplayNameCacheManager.batch_delete_display_name(
                [user.id for user in collaboration_tenant_users], config.version
            )

    @staticmethod
    def batch_delete_display_name_cache(users: List[TenantUser]):
        """批量失效 DisplayName 缓存"""
        # NOTE：这里输入的一定为当前租户用户，因为只有当前租户用户才会触发这个方法

        if not users:
            return

        # 获取协同至其他租户的用户
        data_source_user_ids = [user.data_source_user_id for user in users]
        collaboration_tenant_users = TenantUser.objects.filter(data_source_user_id__in=data_source_user_ids).exclude(
            tenant_id=users[0].tenant_id
        )

        # 删除本租户用户缓存
        config = get_display_name_config(users[0].tenant_id)
        DisplayNameCacheManager.batch_delete_display_name([user.id for user in users], config.version)

        # 删除协同租户用户缓存
        if collaboration_tenant_users:
            config = DisplayNameCacheHandler.build_default_display_name_config()
            DisplayNameCacheManager.batch_delete_display_name(
                [user.id for user in collaboration_tenant_users], config.version
            )
