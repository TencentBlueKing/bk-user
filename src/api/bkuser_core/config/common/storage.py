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
from . import env
from bkuser_global.config import get_db_config

# ==============================================================================
# 数据库
# ==============================================================================
DB_PREFIX = env("DB_PREFIX", default="DB")

DATABASES = get_db_config(env, DB_PREFIX)


# ==============================================================================
# Redis
# ==============================================================================
REDIS_HOST = env("CACHE_REDIS_HOST", default="")
REDIS_PORT = env("CACHE_REDIS_PORT", default="")
REDIS_PASSWORD = env("CACHE_REDIS_PASSWORD", default="")
REDIS_DB = env("CACHE_REDIS_DB", default=0)
REDIS_KEY_PREFIX = env("CACHE_REDIS_KEY_PREFIX", default="bk-user-")

REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# ==============================================================================
# Celery
# ==============================================================================
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = "django-db"
CELERY_TASK_DEFAULT_QUEUE = env("CELERY_TASK_DEFAULT_QUEUE", default="bk_user")


# ==============================================================================
# 缓存配置
# ==============================================================================
CACHES = {
    "default": {
        "BACKEND": "bkuser_core.common.cache.DummyRedisCache",
    },
    "locmem": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "memory_cache_0",
        "KEY_PREFIX": "bk_user",
    },
    "verification_code": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "TIMEOUT": 30 * 60,
        "KEY_PREFIX": f"{REDIS_KEY_PREFIX}verification_code",
        "VERSION": 1,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient", "PASSWORD": REDIS_PASSWORD},
        "SOCKET_CONNECT_TIMEOUT": 5,  # socket 建立连接超时设置，单位秒
        "SOCKET_TIMEOUT": 5,  # 连接建立后的读写操作超时设置，单位秒
        "IGNORE_EXCEPTIONS": True,  # redis 只作为缓存使用, 触发异常不能影响正常逻辑，可能只是稍微慢点而已
    },
}
# 全局缓存过期时间，默认为一小时
GLOBAL_CACHES_TIMEOUT = env.int("GLOBAL_CACHES_TIMEOUT", default=60 * 60)

# 快捷单元测试 dummy cache 标记
USE_DUMMY_CACHE_FOR_TEST = True

FORCE_JSONP_HEADER = "HTTP_FORCE_JSONP"
FORCE_NO_CACHE_HEADER = "HTTP_FORCE_NO_CACHE"
