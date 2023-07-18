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
import os
import hashlib
from urllib.parse import urlparse
from pathlib import Path

import environ

# environ
env = environ.Env()
# load environment variables from .env file
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',
    'corsheaders',
    'django_celery_beat',
    'django_prometheus',
    'bkuser.auth',
    'bkuser.apps.data_source',
    'bkuser.apps.tenant',
]
# Application definition

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'bkuser.common.middlewares.RequestProvider',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'bkuser.auth.middlewares.LoginMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'bkuser.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bkuser.wsgi.application'

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
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Auth
AUTHENTICATION_BACKENDS = ['bkuser.auth.backends.TokenBackend']
AUTH_USER_MODEL = 'bkuser_auth.User'

# Internationalization
LANGUAGE_CODE = 'zh-hans'
LANGUAGE_COOKIE_NAME = 'blueking_language'
LOCALE_PATHS = [BASE_DIR / 'locale']
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'Asia/Shanghai'

# SITE
SITE_URL = '/'
# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR / "staticfiles"
WHITENOISE_STATIC_PREFIX = '/staticfiles/'
STATIC_URL = SITE_URL + 'staticfiles/'

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

# Celery
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
CELERY_IMPORTS = []
# 内置的周期任务
CELERYBEAT_SCHEDULE = {}
# Celery消息队列
BROKER_URL = env.str("BK_BROKER_URL", default="")

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
AJAX_URL_PREFIX = SITE_URL + "api/v1"

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

# Login
LOGIN_SERVICE_URL = env.str("BK_LOGIN_URL", default="/")
# bk esb api url
BK_COMPONENT_API_URL = env.str("BK_COMPONENT_API_URL")

# 日志配置
LOG_LEVEL = env.str("LOG_LEVEL", default="ERROR")
_LOG_CLASS = "logging.handlers.RotatingFileHandler"
_DEFAULT_LOG_DIR = BASE_DIR.parent / "logs" / BK_APP_CODE
_LOG_DIR = env.str("LOG_FILE_DIR", default=_DEFAULT_LOG_DIR)
_LOG_FILE_NAME_PREFIX = env.str("LOG_FILE_NAME_PREFIX", default=BK_APP_CODE)
if not os.path.exists(_LOG_DIR):
    os.makedirs(_LOG_DIR)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": (
                "%(levelname)s %(asctime)s %(pathname)s %(lineno)d " "%(funcName)s %(process)d %(thread)d %(message)s"
            ),
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "simple"},
        "root": {
            "class": _LOG_CLASS,
            "formatter": "verbose",
            "filename": os.path.join(_LOG_DIR, "%s-django.log" % _LOG_FILE_NAME_PREFIX),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
        },
        "component": {
            "class": _LOG_CLASS,
            "formatter": "verbose",
            "filename": os.path.join(_LOG_DIR, "%s-component.log" % _LOG_FILE_NAME_PREFIX),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
        },
        "mysql": {
            "class": _LOG_CLASS,
            "formatter": "verbose",
            "filename": os.path.join(_LOG_DIR, "%s-mysql.log" % _LOG_FILE_NAME_PREFIX),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
        },
        "celery": {
            "class": _LOG_CLASS,
            "formatter": "verbose",
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
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "django.request": {
            "handlers": ["root"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["mysql"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        # the root logger ,用于整个project的logger
        "root": {
            "handlers": ["root"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        # 组件调用日志
        "component": {
            "handlers": ["component"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "celery": {
            "handlers": ["celery"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        # 普通app日志
        "app": {
            "handlers": ["root"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
    },
}
