# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 用户管理 (Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import ssl

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

# redis tls
REDIS_TLS_ENABLED = env.bool("CACHE_REDIS_TLS_ENABLED", False)
REDIS_TLS_CERT_CA_FILE = env.str("CACHE_REDIS_TLS_CERT_CA_FILE", default="")
REDIS_TLS_CERT_FILE = env.str("CACHE_REDIS_TLS_CERT_FILE", default="")
REDIS_TLS_CERT_KEY_FILE = env.str("CACHE_REDIS_TLS_CERT_KEY_FILE", default="")

# 根据是否启用 TLS 使用不同的协议: rediss:// (TLS) 或 redis:// (无加密)
REDIS_PROTOCOL = "rediss" if REDIS_TLS_ENABLED else "redis"
REDIS_URL = f"{REDIS_PROTOCOL}://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# redis sentinel配置
REDIS_SENTINEL = env.bool("CACHE_REDIS_SENTINEL_ENABLED", False)
REDIS_SENTINEL_MASTER_NAME = env("CACHE_REDIS_SENTINEL_MASTER_NAME", default="")
REDIS_SENTINEL_PASSWORD = env("CACHE_REDIS_SENTINEL_PASSWORD", default="")
REDIS_SENTINEL_NODES = env.list("CACHE_REDIS_SENTINEL_NODES", default=[])

# ==============================================================================
# Celery
# ==============================================================================
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = "django-db"
CELERY_TASK_DEFAULT_QUEUE = env("CELERY_TASK_DEFAULT_QUEUE", default="bk_user")

# 如果启用了 Celery Broker TLS 且 URL 是 Redis，自动转换为 rediss:// 协议
if REDIS_TLS_ENABLED and CELERY_BROKER_URL.startswith("redis://"):
    CELERY_BROKER_URL = CELERY_BROKER_URL.replace("redis://", "rediss://", 1)

# Celery sentinel配置
if REDIS_SENTINEL and REDIS_SENTINEL_NODES:
    # 转换 Sentinel 节点格式
    sentinel_nodes = []
    for node in REDIS_SENTINEL_NODES:
        host, port = node.split(":")
        sentinel_nodes.append((host, int(port)))

    # 更新 Celery broker URL
    CELERY_BROKER_URL = (
        f"sentinel://:{REDIS_PASSWORD}@{';'.join(REDIS_SENTINEL_NODES)}"
        f"/{REDIS_DB}"
    )

    # 添加 Sentinel 配置
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        "master_name": REDIS_SENTINEL_MASTER_NAME,
        "sentinel_kwargs": {"password": REDIS_SENTINEL_PASSWORD},
    }

    # 如果启用 TLS
    if REDIS_TLS_ENABLED:
        CELERY_BROKER_TRANSPORT_OPTIONS.update({
            "ssl_cert_reqs": ssl.CERT_REQUIRED,
            "ssl_ca_certs": REDIS_TLS_CERT_CA_FILE,
            "visibility_timeout": 3600,
            "fanout_prefix": True,
            "socket_timeout": 5,
            "retry_policy": {
                "interval_start": 0,
                "interval_step": 0.2,
                "max_retries": 3,
            },
        })
        if REDIS_TLS_CERT_FILE and REDIS_TLS_CERT_KEY_FILE:
            CELERY_BROKER_TRANSPORT_OPTIONS.update({
                "ssl_certfile": REDIS_TLS_CERT_FILE,
                "ssl_keyfile": REDIS_TLS_CERT_KEY_FILE,
            })
    CELERY_TASK_ACKS_LATE = True
    CELERY_TASK_REJECT_ON_WORKER_LOST = True
else:
    # celery broker tls : 仅仅支持 rabbitmq 和 单例 redis 作为 celery broker 时开启 TLS
    if CELERY_BROKER_URL and REDIS_TLS_ENABLED:
        ssl_key_prefix = "ssl_" if CELERY_BROKER_URL.startswith("redis") else ""
        CELERY_BROKER_USE_SSL = {
            f"{ssl_key_prefix}cert_reqs": ssl.CERT_REQUIRED,
            f"{ssl_key_prefix}ca_certs": REDIS_TLS_CERT_CA_FILE,
        }
        # mTLS
        if REDIS_TLS_CERT_FILE and REDIS_TLS_CERT_KEY_FILE:
            CELERY_BROKER_USE_SSL[f"{ssl_key_prefix}certfile"] = REDIS_TLS_CERT_FILE
            CELERY_BROKER_USE_SSL[f"{ssl_key_prefix}keyfile"] = REDIS_TLS_CERT_KEY_FILE
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
        "TIMEOUT": 60,
        "KEY_PREFIX": "bk_user",
    },
    "verification_code": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "TIMEOUT": 30 * 60,
        "KEY_PREFIX": f"{REDIS_KEY_PREFIX}verification_code",
        "VERSION": 1,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": REDIS_PASSWORD,
            "SOCKET_TIMEOUT": 3,  # 更短的超时时间
            "WRITE_RETRY": True,  # 启用写入重试
            "WRITE_RETRY_DELAY": 0.1,  # 重试间隔
            "WRITE_RETRY_ATTEMPTS": 3,  # 重试次数
        },
        "SOCKET_CONNECT_TIMEOUT": 5,  # socket 建立连接超时设置，单位秒
        "IGNORE_EXCEPTIONS": True,  # redis 只作为缓存使用，触发异常不能影响正常逻辑，可能只是稍微慢点而已
    },
}
# 全局缓存过期时间，默认为一小时
GLOBAL_CACHES_TIMEOUT = env.int("GLOBAL_CACHES_TIMEOUT", default=60 * 60)

# redis sentinel配置
if REDIS_SENTINEL and REDIS_SENTINEL_NODES:
    # Sentinel 模式配置
    sentinel_nodes = []
    for node in REDIS_SENTINEL_NODES:
        host, port = node.split(":")
        sentinel_nodes.append((host, int(port)))

    CACHES["verification_code"] = {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        "TIMEOUT": 30 * 60,
        "KEY_PREFIX": f"{REDIS_KEY_PREFIX}verification_code",
        "VERSION": 1,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.SentinelClient",
            "SENTINELS": sentinel_nodes,
            "SENTINEL_KWARGS": {
                "password": REDIS_SENTINEL_PASSWORD,
            },
            "MASTER_NAME": REDIS_SENTINEL_MASTER_NAME,
            "PASSWORD": REDIS_PASSWORD,
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "IGNORE_EXCEPTIONS": True,
        },
    }

    # 如果启用 TLS
    if REDIS_TLS_ENABLED:
        # Sentinel 模式下使用 rediss:// 协议
        CACHES["verification_code"]["LOCATION"] = f"rediss://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
        CACHES["verification_code"]["OPTIONS"]["CONNECTION_POOL_KWARGS"] = {
            "ssl_cert_reqs": ssl.CERT_REQUIRED,
            "ssl_ca_certs": REDIS_TLS_CERT_CA_FILE,
        }
        if REDIS_TLS_CERT_FILE and REDIS_TLS_CERT_KEY_FILE:
            CACHES["verification_code"]["OPTIONS"]["CONNECTION_POOL_KWARGS"].update({
                "ssl_certfile": REDIS_TLS_CERT_FILE,
                "ssl_keyfile": REDIS_TLS_CERT_KEY_FILE,
            })
else:
    # redis tls : 仅仅支持 redis 单例模式
    if REDIS_TLS_ENABLED:
        # 单例模式下使用 rediss:// 协议(已通过 REDIS_URL 自动处理)
        CACHES["verification_code"]["LOCATION"] = REDIS_URL

        if "CONNECTION_POOL_KWARGS" not in CACHES["verification_code"]["OPTIONS"]:
            CACHES["verification_code"]["OPTIONS"]["CONNECTION_POOL_KWARGS"] = {}

        CACHES["verification_code"]["OPTIONS"]["CONNECTION_POOL_KWARGS"]["ssl_cert_reqs"] = ssl.CERT_REQUIRED
        CACHES["verification_code"]["OPTIONS"]["CONNECTION_POOL_KWARGS"]["ssl_ca_certs"] = REDIS_TLS_CERT_CA_FILE
        # mTLS
        if REDIS_TLS_CERT_FILE and REDIS_TLS_CERT_KEY_FILE:
            CACHES["verification_code"]["OPTIONS"]["CONNECTION_POOL_KWARGS"]["ssl_certfile"] = REDIS_TLS_CERT_FILE
            CACHES["verification_code"]["OPTIONS"]["CONNECTION_POOL_KWARGS"]["ssl_keyfile"] = REDIS_TLS_CERT_KEY_FILE
# 快捷单元测试 dummy cache 标记
USE_DUMMY_CACHE_FOR_TEST = True

FORCE_JSONP_HEADER = "HTTP_FORCE_JSONP"
FORCE_NO_CACHE_HEADER = "HTTP_FORCE_NO_CACHE"
