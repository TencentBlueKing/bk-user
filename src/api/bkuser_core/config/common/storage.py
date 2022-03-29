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
from bkuser_global.config import get_db_config

from . import env

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
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")
CELERY_TASK_DEFAULT_QUEUE = env("CELERY_TASK_DEFAULT_QUEUE", default="bk_user")


# ==============================================================================
# 缓存配置
# ==============================================================================
CACHES = {
    "default": {
        "BACKEND": "bkuser_core.common.cache.DummyRedisCache",
    },
    'locmem': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'memory_cache_0',
    },
}
# 全局缓存过期时间，默认为一小时
GLOBAL_CACHES_TIMEOUT = env.int("GLOBAL_CACHES_TIMEOUT", default=60 * 60)

# 快捷单元测试 dummy cache 标记
USE_DUMMY_CACHE_FOR_TEST = True

FORCE_JSONP_HEADER = "HTTP_FORCE_JSONP"
FORCE_NO_CACHE_HEADER = "HTTP_FORCE_NO_CACHE"
