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
import logging

from django.conf import settings
from django.core.cache import caches
from django.core.cache.backends.dummy import DummyCache

logger = logging.getLogger(__name__)


# =========================================
# legacy codes, will be removed after refactor
# =========================================

CACHE_KEYWORD = "views.decorators.cache*"


def clear_cache(cache_name: str = "default"):
    """清理某个 key 的缓存"""
    logger.info("going to clear cache %s", cache_name)
    target_cache = caches[cache_name]

    # why not cache.clear() ?
    # because tendis doesn't support FLUSHDB command
    # flushdb is dangerous if redis db is shared
    target_cache.delete_pattern(CACHE_KEYWORD, prefix=settings.REDIS_KEY_PREFIX)


def clear_cache_if_succeed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        value = func(*args, **kwargs)
        # due to multiple relations, it's complex to clear every resource individually.
        # so clear all cache for now
        clear_cache()

        return value

    return wrapper


class DummyRedisCache(DummyCache):
    def __init__(self, server, params):
        super().__init__(server, params)
        self._client = None
        self._ignore_exceptions = True

    @property
    def client(self):
        """
        Lazy client connection property.
        """
        return None

    def delete_pattern(self, *args, **kwargs):
        """Dummy delete pattern"""
        return 0

    def keys(self, *args, **kwargs):
        """Dummy keys"""
        return []

    def iter_keys(self, *args, **kwargs):
        """Dummy iter_keys"""
        yield None

    def ttl(self, *args, **kwargs):
        """Dummy ttl"""
        return None

    def persist(self, *args, **kwargs):
        """Dummy persist"""

    def expire(self, *args, **kwargs):
        """Dummy expire"""

    def lock(self, *args, **kwargs):
        """Dummy lock"""
        return None

    def touch(self, key, timeout=None, version=None):
        """Dummy touch"""
        return None
