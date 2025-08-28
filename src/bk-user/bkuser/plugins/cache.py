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


from blue_krill.data_types.enum import EnumField, StrStructuredEnum
from django.core.cache import caches
from django.core.cache.backends.base import DEFAULT_TIMEOUT


class CacheEnum(StrStructuredEnum):
    """枚举可用的 Cache，与 settings.Cache 配置的 Dict.keys 一致"""

    DEFAULT = EnumField("default", label="内存缓存（默认）")
    REDIS = EnumField("redis", label="Redis 缓存")


# 项目里不同场景的缓存实现都分散在各处，实现缓存中可能出现不同场景缓存 key 冲突问题，
# 为避免该问题，所以缓存场景都必须在这里定义其 Key 的前缀
# 完整 Key = [全局前缀]settings.Caches.KEY_PREFIX + [全局版本]settings.Caches.VERSION + CacheKeyPrefixEnum + CustomKey
# 注意：KeyPrefix 应不互相冲突且尽可能短，不需要优先考虑可读性
class CacheKeyPrefixEnum(StrStructuredEnum):
    # 用于使用 cached 和 cachedmethod 装饰器自动生成 key 的
    AUTO = "auto"
    # 企业微信 API access_token
    WECOM_API_ACCESS_TOKEN = "wecom_api_access_token"


class Cache:
    """
    Cache 用于避免直接使用 Django Caches 时导致不同场景的前缀 Key 冲突问题，
    使用各个场景更专注于自身业务逻辑缓存和 key 生成，Cache 所有方法都基于
    Django Cache 的 BaseCache ，只封装了项目所需方法
    """

    def __init__(self, type_, key_prefix):
        self.cache = caches[type_]
        self.type = type_
        self.key_prefix = key_prefix
        # 支持获取锁的特性
        self.lock_supported = type_ in [CacheEnum.REDIS]

    def _make_key(self, key):
        return f"{self.key_prefix}:{key}"

    def get(self, key, default=None, version=None):
        key = self._make_key(key)
        return self.cache.get(key, default, version)

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        key = self._make_key(key)
        self.cache.set(key, value, timeout, version)

    def delete(self, key, version=None):
        key = self._make_key(key)
        self.cache.delete(key, version)

    def get_many(self, keys, version=None):
        if not keys:
            return {}

        map_keys = {self._make_key(k): k for k in keys}

        results = self.cache.get_many(map_keys.keys(), version)

        data = {}
        for key in map_keys:
            if key not in results:
                continue
            data[map_keys[key]] = results[key]
        return data

    def set_many(self, data, timeout=DEFAULT_TIMEOUT, version=None):
        map_key_data = {self._make_key(key): value for key, value in data.items()}
        self.cache.set_many(map_key_data, timeout, version)

    def lock(self, key, version=None, timeout=None, sleep=0.1, blocking_timeout=None, client=None):
        if not self.lock_supported:
            raise NotImplementedError(f"{self.type} cache not support lock")

        key = self._make_key(key)
        return self.cache.lock(key, version, timeout, sleep, blocking_timeout, client)
