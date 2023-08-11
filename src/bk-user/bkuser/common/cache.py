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
import functools

from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.core.cache import cache as default_cache
from django.core.cache import caches
from django.core.cache.backends.base import DEFAULT_TIMEOUT


class CacheEnum(str, StructuredEnum):
    """枚举可用的 Cache，与 settings.Cache 配置的 Dict.keys 一致"""

    DEFAULT = EnumField("default", label="内存缓存（默认）")
    REDIS = EnumField("redis", label="Redis 缓存")


# 项目里不同场景的缓存实现都分散在各处，实现缓存中可能出现不同场景缓存 key 冲突问题，
# 为避免该问题，所以缓存场景都必须在这里定义其 Key 的前缀
# 完整 Key = [全局前缀]settings.Caches.KEY_PREFIX + [全局版本]settings.Caches.VERSION + CacheKeyPrefixEnum + CustomKey
class CacheKeyPrefixEnum(str, StructuredEnum):
    # 用于使用 cached 和 cachedmethod 装饰器自动生成 key 的
    AUTO = "auto"
    # 分布式锁
    LOCK = "lock"


def _default_key_function(*args, **kwargs):
    """
    Return a string key, based on a given args and kwargs
    """
    key = "|".join(map(str, args))
    if kwargs:
        key += "|" + "|".join(map(str, sorted(kwargs.items())))

    return key


def _method_key_function(_, *args, **kwargs):
    return _default_key_function(*args, **kwargs)


# cached 和 cachedmethod 其 key 的生成方法可以满足大部分情况下不冲突，但有以下几种情况可能会冲突
# (1) 对于类的实例方法，由于缓存 key 只用到方法的自定义参数，
#     若 key 的区分需要用到 self.{attr}，则需要重新自定义，否则相同方法参数时会冲突
# (2) 虽然模块名+方法名作为了 key 的前缀，但由于是字符串拼接，
#     有极少概率会出现拼接出来的结果一样的情况而导致冲突
# (3) key 的字符串拼接，若参数里的值包含分隔符 "|"，有可能出现冲突
# (4) 生成 key 时做了字符串转换，对于某些对象可能 str() 后相同，
#     建议参数类型为：str/bool/int/tuple/List[base_type]/Dict[base_type]
def cached(cache=default_cache, key_function=_default_key_function, timeout=DEFAULT_TIMEOUT):
    """Decorator to wrap a function with a memorizing callable that saves results in a cache.
    cache param usage:
        from django.core.cache import caches
        @cached(cache=caches[CacheEnum.REDIS], ...)
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            custom_key = key_function(*args, **kwargs)
            namespace = f"{func.__module__}:{func.__name__}"
            key = f"{CacheKeyPrefixEnum.AUTO}:{namespace}:{custom_key}"

            return cache.get_or_set(key, lambda: func(*args, **kwargs), timeout)

        return wrapper

    return decorator


def cachedmethod(cache=default_cache, key_function=_method_key_function, timeout=DEFAULT_TIMEOUT):
    """Decorator to wrap a class or instance method with a memorizing
    callable that saves results in a cache.
    """

    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            custom_key = key_function(self, *args, **kwargs)
            namespace = f"{method.__module__}:{method.__qualname__}"
            key = f"{CacheKeyPrefixEnum.AUTO}:{namespace}:{custom_key}"

            return cache.get_or_set(key, lambda: method(self, *args, **kwargs), timeout)

        return wrapper

    return decorator


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
