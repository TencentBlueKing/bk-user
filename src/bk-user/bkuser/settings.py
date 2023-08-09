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
import hashlib
import os
from pathlib import Path
from urllib.parse import urlparse

import environ
import urllib3

# environ
env = environ.Env()
# load environment variables from .env file
environ.Env.read_env()

# no more useless warning
urllib3.disable_warnings()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", False)
IS_LOCAL = env.bool("IS_LOCAL", default=False)

ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "django_celery_beat",
    "django_prometheus",
    "drf_yasg",
    "bkuser.auth",
    "bkuser.apps.data_source",
    "bkuser.apps.tenant",
    "bkuser.apps.data_source_organization",
    "bkuser.apps.tenant_organization",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "bkuser.common.middlewares.RequestProvider",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "bkuser.auth.middlewares.LoginMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "bkuser.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "bkuser.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.str("MYSQL_NAME"),
        "USER": env.str("MYSQL_USER"),
        "PASSWORD": env.str("MYSQL_PASSWORD"),
        "HOST": env.str("MYSQL_HOST"),
        "PORT": env.int("MYSQL_PORT"),
    },
}
# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth
AUTHENTICATION_BACKENDS = ["bkuser.auth.backends.TokenBackend"]
AUTH_USER_MODEL = "bkuser_auth.User"

# Internationalization
LANGUAGE_CODE = "zh-hans"
LANGUAGE_COOKIE_NAME = "blueking_language"
LOCALE_PATHS = [BASE_DIR / "locale"]
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = "Asia/Shanghai"

# SITE
SITE_URL = "/"
# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR / "staticfiles"
WHITENOISE_STATIC_PREFIX = "/staticfiles/"
# STATIC_URL 也可以是CDN地址
STATIC_URL = env.str("STATIC_URL", SITE_URL + "staticfiles/")

# cookie
SESSION_COOKIE_NAME = "bkuser_sessionid"
SESSION_COOKIE_AGE = 60 * 60 * 24  # 1天

# rest_framework
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "bkuser.common.views.custom_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "bkuser.common.pagination.CustomPageNumberPagination",
    "PAGE_SIZE": 10,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["bkuser.common.renderers.BkStandardApiJSONRenderer"],
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
}
SWAGGER_ENABLE = env.bool("SWAGGER_ENABLE", default=False)
SWAGGER_SETTINGS = {
    "DEFAULT_AUTO_SCHEMA_CLASS": "bkuser.common.swagger.BkStandardResponseSwaggerAutoSchema",
}

# Requests pool config
REQUESTS_POOL_CONNECTIONS = env.int("REQUESTS_POOL_CONNECTIONS", default=20)
REQUESTS_POOL_MAXSIZE = env.int("REQUESTS_POOL_MAXSIZE", default=20)

BK_APP_CODE = env.str("BK_APP_CODE", default="bkuser")
BK_APP_SECRET = env.str("BK_APP_SECRET")
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = BK_APP_SECRET

# bk_language domain
BK_DOMAIN = env.str("BK_DOMAIN", default="")
# BK USER URL
BK_USER_URL = env.str("BK_USER_URL")
AJAX_BASE_URL = SITE_URL + "api/v1"

# csrf
_BK_USER_URL_PARSE_URL = urlparse(BK_USER_URL)
_BK_USER_HOSTNAME = _BK_USER_URL_PARSE_URL.hostname  # 去除端口的域名
_BK_USER_NETLOC = _BK_USER_URL_PARSE_URL.netloc  # 若有端口，则会带上对应端口
_BK_USER_IS_SPECIAL_PORT = _BK_USER_URL_PARSE_URL.port in [None, 80, 443]
_BK_USER_SCHEME = _BK_USER_URL_PARSE_URL.scheme
_BK_USER_URL_MD5_16BIT = hashlib.md5(BK_USER_URL.encode("utf-8")).hexdigest()[8:-8]
# 注意：Cookie Domain是不支持端口的
SESSION_COOKIE_DOMAIN = _BK_USER_HOSTNAME
CSRF_COOKIE_DOMAIN = SESSION_COOKIE_DOMAIN
CSRF_COOKIE_NAME = f"bkuser_csrftoken_{_BK_USER_URL_MD5_16BIT}"
# 对于特殊端口，带端口和不带端口都得添加，其他只需要添加默认原生的即可
CSRF_TRUSTED_ORIGINS = [_BK_USER_HOSTNAME, _BK_USER_NETLOC] if _BK_USER_IS_SPECIAL_PORT else [_BK_USER_NETLOC]

# cors
CORS_ALLOW_CREDENTIALS = True  # 在 response 添加 Access-Control-Allow-Credentials, 即允许跨域使用 cookies
CORS_ORIGIN_WHITELIST = (
    [f"{_BK_USER_SCHEME}://{_BK_USER_HOSTNAME}", f"{_BK_USER_SCHEME}://{_BK_USER_NETLOC}"]
    if _BK_USER_IS_SPECIAL_PORT
    else [f"{_BK_USER_SCHEME}://{_BK_USER_NETLOC}"]
)
# debug/联调测试时需要允许额外的域名跨域请求
CORS_ORIGIN_ADDITIONAL_WHITELIST = env.list("CORS_ORIGIN_ADDITIONAL_WHITELIST", default=[])
CORS_ORIGIN_WHITELIST.extend(CORS_ORIGIN_ADDITIONAL_WHITELIST)

# Login
BK_LOGIN_URL = env.str("BK_LOGIN_URL", default="/")
# bk esb api url
BK_COMPONENT_API_URL = env.str("BK_COMPONENT_API_URL")

# ------------------------------------------ Celery 配置 ------------------------------------------

# 连接 BROKER 超时时间
BROKER_CONNECTION_TIMEOUT = 1  # 单位秒
# CELERY与RabbitMQ增加60秒心跳设置项
BROKER_HEARTBEAT = 60
# CELERY 并发数，默认为 2，可以通过环境变量或者 Procfile 设置
CELERYD_CONCURRENCY = env.int("CELERYD_CONCURRENCY", default=2)
# 与周期任务配置的定时相关UTC
CELERY_ENABLE_UTC = False
# 周期任务beat生产者来源
CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
# 任务结果存储
CELERY_RESULT_BACKEND = "django-db"
# Celery队列名称
CELERY_DEFAULT_QUEUE = "bkuser"
# close celery hijack root logger
CELERYD_HIJACK_ROOT_LOGGER = False
# disable remote control
CELERY_ENABLE_REMOTE_CONTROL = False
# Celery 消息序列化
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
# CELERY 配置，申明任务的文件路径，即包含有 @task 装饰器的函数文件
# CELERY_IMPORTS = []
# 内置的周期任务
# CELERYBEAT_SCHEDULE = {}
# Celery消息队列
BROKER_URL = env.str("BK_BROKER_URL", default="")

# ------------------------------------------ 缓存配置 ------------------------------------------

REDIS_HOST = env.str("REDIS_HOST", "localhost")
REDIS_PORT = env.int("REDIS_PORT", 6379)
REDIS_PASSWORD = env.str("REDIS_PASSWORD", "")
REDIS_MAX_CONNECTIONS = env.int("REDIS_MAX_CONNECTIONS", 100)
REDIS_DB = env.int("REDIS_DB", 0)

REDIS_USE_SENTINEL = env.bool("REDIS_USE_SENTINEL", False)
REDIS_SENTINEL_MASTER_NAME = env.str("REDIS_SENTINEL_MASTER_NAME", "master")
REDIS_SENTINEL_PASSWORD = env.str("REDIS_SENTINEL_PASSWORD", "")
REDIS_SENTINEL_ADDR_STR = env.str("REDIS_SENTINEL_ADDR", "")
# parse sentinel address from "host1:port1,host2:port2" to [("host1", port1), ("host2", port2)]
REDIS_SENTINEL_ADDR_LIST = []
try:
    REDIS_SENTINEL_ADDR_LIST = [tuple(addr.split(":")) for addr in REDIS_SENTINEL_ADDR_STR.split(",") if addr]
except Exception as e:  # pylint: disable=broad-except
    print(f"REDIS_SENTINEL_ADDR {REDIS_SENTINEL_ADDR_STR} is invalid: {e}")

CACHES = {
    # 默认缓存是本地内存，使用最近最少使用（LRU）的淘汰策略，使用 pickle 序列化数据
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        # 多个本地内存缓存时才需要设置
        "LOCATION": "",
        # 默认过期时间：30 min
        "TIMEOUT": 60 * 30,
        # 缓存的 Key 前缀
        "KEY_PREFIX": "bkuser",
        # 内存缓存特有参数
        "OPTIONS": {
            # 支持缓存的 key 最多数量，越大将会占用更多内存
            "MAX_ENTRIES": 1000,
            # 当达到 MAX_ENTRIES 时被淘汰的部分条目，淘汰率是 1 / CULL_FREQUENCY，默认淘汰 1/3 的缓存 key
            "CULL_FREQUENCY": 3,
        },
    },
    "redis": {
        "BACKEND": "django_redis.cache.RedisCache",
        # 若需要支持主从配置，则 LOCATION 为 List[master_url, slave_url]
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        # 默认过期时间：30 min
        "TIMEOUT": 60 * 30,
        # 缓存的 Key 前缀
        "KEY_PREFIX": "bkuser",
        # 避免同缓存 Key 在不同 SaaS 版本之间存在差异导致读取的值非期望的
        "VERSION": 3,
        "OPTIONS": {
            # Sentinel 模式 django_redis.client.SentinelClient (django-redis>=5.0.0)
            # 集群模式 django_redis.client.HerdClient
            # 单实例模式 django_redis.client.DefaultClient
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": REDIS_PASSWORD,
            # socket 建立连接超时设置，单位秒
            "SOCKET_CONNECT_TIMEOUT": 5,
            # 连接建立后的读写操作超时设置，单位秒
            "SOCKET_TIMEOUT": 5,
            # redis 只作为缓存使用, 触发异常不能影响正常逻辑，可能只是稍微慢点而已
            "IGNORE_EXCEPTIONS": True,
            # 默认使用 pickle 序列化数据，可选序列化方式有：pickle、json、msgpack
            # "SERIALIZER": "django_redis.serializers.pickle.PickleSerializer"
            # Redis 连接池配置
            "CONNECTION_POOL_KWARGS": {
                # redis-py 默认不会关闭连接, 可能会造成连接过多，导致 Redis 无法服务，因此需要设置最大值连接数
                "max_connections": REDIS_MAX_CONNECTIONS
            },
        },
    },
}

# redis sentinel
if REDIS_USE_SENTINEL:
    # Enable the alternate connection factory.
    DJANGO_REDIS_CONNECTION_FACTORY = "django_redis.pool.SentinelConnectionFactory"

    CACHES["redis"] = {
        "BACKEND": "django_redis.cache.RedisCache",
        # The hostname in LOCATION is the primary (service / master) name
        "LOCATION": f"redis://{REDIS_SENTINEL_MASTER_NAME}/{REDIS_DB}",
        # 默认过期时间：30 min
        "TIMEOUT": 60 * 30,
        # 缓存的Key的前缀
        "KEY_PREFIX": "bkuser",
        # 避免同缓存 Key 在不同 SaaS 版本之间存在差异导致读取的值非期望的
        "VERSION": 3,
        "OPTIONS": {
            # While the default client will work, this will check you
            # have configured things correctly, and also create a
            # primary and replica pool for the service specified by
            # LOCATION rather than requiring two URLs.
            "CLIENT_CLASS": "django_redis.client.SentinelClient",
            "PASSWORD": REDIS_PASSWORD,
            # socket 建立连接超时设置，单位秒
            "SOCKET_CONNECT_TIMEOUT": 5,
            # 连接建立后的读写操作超时设置，单位秒
            "SOCKET_TIMEOUT": 5,
            # redis 只作为缓存使用, 触发异常不能影响正常逻辑，可能只是稍微慢点而已
            "IGNORE_EXCEPTIONS": True,
            # Sentinels which are passed directly to redis Sentinel.
            "SENTINELS": REDIS_SENTINEL_ADDR_LIST,
            # kwargs for redis Sentinel (optional).
            "SENTINEL_KWARGS": {
                "password": REDIS_SENTINEL_PASSWORD,
                "socket_timeout": 5,
            },
            # You can still override the connection pool (optional).
            "CONNECTION_POOL_CLASS": "redis.sentinel.SentinelConnectionPool",
            # Redis 连接池配置
            "CONNECTION_POOL_KWARGS": {
                # redis-py 默认不会关闭连接, 可能会造成连接过多，导致 Redis 无法服务，因此需要设置最大值连接数
                "max_connections": REDIS_MAX_CONNECTIONS
            },
        },
    }

    # celery broker
    # https://docs.celeryq.dev/en/v4.3.0/history/whatsnew-4.0.html?highlight=sentinel#redis-support-for-sentinel
    if not BROKER_URL:
        BROKER_URL = ";".join(
            [f"sentinel://:{REDIS_PASSWORD}@" + ":".join(addr) + f"/{REDIS_DB}" for addr in REDIS_SENTINEL_ADDR_LIST]
        )
        BROKER_TRANSPORT_OPTIONS = {
            "master_name": REDIS_SENTINEL_MASTER_NAME,
            "sentinel_kwargs": {"password": REDIS_SENTINEL_PASSWORD},
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
            "socket_keepalive": True,
        }

# 当 Redis Cache 使用 IGNORE_EXCEPTIONS 时，设置指定的 logger 输出异常
DJANGO_REDIS_LOGGER = "root"

# ------------------------------------------ 日志配置 ------------------------------------------

# 日志配置
LOG_LEVEL = env.str("LOG_LEVEL", default="ERROR")
_LOG_CLASS = "logging.handlers.RotatingFileHandler"
_DEFAULT_LOG_DIR = BASE_DIR / "logs"
_LOG_DIR = env.str("LOG_FILE_DIR", default=_DEFAULT_LOG_DIR)
_LOG_FILE_NAME_PREFIX = env.str("LOG_FILE_NAME_PREFIX", default=BK_APP_CODE)
if not os.path.exists(_LOG_DIR):
    os.makedirs(_LOG_DIR)
_LOGGING_FORMAT = {
    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
    "fmt": ("%(levelname)s %(asctime)s %(pathname)s %(lineno)d " "%(funcName)s %(process)d %(thread)d %(message)s"),
}
if IS_LOCAL:
    _LOGGING_FORMAT = {
        "format": (
            "%(levelname)s [%(asctime)s] %(pathname)s "
            "%(lineno)d %(funcName)s %(process)d %(thread)d "
            "\n \t%(message)s \n"
        ),
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id_filter": {
            "()": "bkuser.common.log.RequestIDFilter",
        }
    },
    "formatters": {
        "verbose": _LOGGING_FORMAT,
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "null": {"level": "DEBUG", "class": "logging.NullHandler"},
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "simple"},
        "root": {
            "class": _LOG_CLASS,
            "formatter": "verbose",
            "filters": ["request_id_filter"],
            "filename": os.path.join(_LOG_DIR, "%s-django.log" % _LOG_FILE_NAME_PREFIX),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
        },
        "component": {
            "class": _LOG_CLASS,
            "formatter": "verbose",
            "filters": ["request_id_filter"],
            "filename": os.path.join(_LOG_DIR, "%s-component.log" % _LOG_FILE_NAME_PREFIX),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
        },
        "celery": {
            "class": _LOG_CLASS,
            "formatter": "verbose",
            "filters": ["request_id_filter"],
            "filename": os.path.join(_LOG_DIR, "%s-celery.log" % _LOG_FILE_NAME_PREFIX),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["null"],
            "level": "INFO",
            "propagate": True,
        },
        "django.server": {
            "handlers": ["root", "console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django.request": {
            "handlers": ["root", "console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        # the root logger, 用于整个项目的 logger
        "root": {
            "handlers": ["root", "console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        # 组件调用日志
        "component": {
            "handlers": ["component", "console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "celery": {
            "handlers": ["celery", "console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}

# ------------------------------------------ Healthz 配置 ------------------------------------------

# 调用 Healthz API 需要的 Token
HEALTHZ_TOKEN = env.str("HEALTHZ_TOKEN", "")
# 服务健康探针配置
HEALTHZ_PROBES = env.list(
    "HEALTHZ_PROBES",
    default=[
        "bkuser.monitoring.healthz.probes.MysqlProbe",
    ],
)

# ------------------------------------------ Metric 配置 ------------------------------------------

# 调用 Metric API 需要的 Token
METRIC_TOKEN = env.str("METRIC_TOKEN", "")

# ------------------------------------------ Tracing 配置 ------------------------------------------

# Sentry DSN 配置
SENTRY_DSN = env.str("SENTRY_DSN", "")

# 是否开启 OTEL 数据上报，默认不启用
ENABLE_OTEL_TRACE = env.bool("ENABLE_OTEL_TRACE", False)
# 上报数据服务名称，一般使用默认值即可
OTEL_SERVICE_NAME = env.str("OTEL_SERVICE_NAME", "bk-user")
# sdk 采样规则（always_on / always_off ...）
OTEL_SAMPLER = env.str("OTEL_SAMPLER", "always_on")
# OTEL 上报地址（grpc）
OTEL_GRPC_URL = env.str("OTEL_GRPC_URL", "")
# OTEL 上报到监控平台的数据 Token，可通过监控平台上新建应用获得
OTEL_DATA_TOKEN = env.str("OTEL_DATA_TOKEN", "")
# 是否记录 DB 相关 tracing
OTEL_INSTRUMENT_DB_API = env.bool("OTEL_INSTRUMENT_DB_API", False)

if ENABLE_OTEL_TRACE or SENTRY_DSN:
    INSTALLED_APPS += ("bkuser.monitoring.tracing",)

# ------------------------------------------ 业务逻辑配置 ------------------------------------------

# 数据源插件默认Logo，值为base64格式图片数据
DATA_SOURCE_PLUGIN_DEFAULT_LOGO = ""
# 租户默认Logo，值为base64格式图片数据
TENANT_DEFAULT_LOGO = ""
# 数据源用户默认Logo，值为base64格式图片数据
DATA_SOURCE_USER_DEFAULT_LOGO = ""
