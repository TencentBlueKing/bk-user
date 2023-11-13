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
from pathlib import Path

import environ
import urllib3
from django.utils.encoding import force_bytes

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
    "bklogin.authentication",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "bklogin.common.middlewares.ExceptionHandlerMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "bklogin.urls"

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
                "bklogin.common.context_processors.basic_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "bklogin.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.str("MYSQL_NAME", "bk-login"),
        "USER": env.str("MYSQL_USER", "root"),
        "PASSWORD": env.str("MYSQL_PASSWORD", ""),
        "HOST": env.str("MYSQL_HOST", "localhost"),
        "PORT": env.int("MYSQL_PORT", 3306),
        "TEST": {
            "CHARSET": "utf8mb4",
        },
    },
}
# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Internationalization
LANGUAGE_CODE = "zh-hans"
LANGUAGE_COOKIE_NAME = "blueking_language"
LOCALE_PATHS = [BASE_DIR / "locale"]
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = "Asia/Shanghai"

# SITE
SITE_URL = env.str("SITE_URL", default="/")
# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR / "staticfiles"
WHITENOISE_STATIC_PREFIX = "/staticfiles/"
# STATIC_URL 也可以是CDN地址
STATIC_URL = env.str("STATIC_URL", default=SITE_URL + "staticfiles/")

# 登录服务的AppCode/AppSecret
BK_APP_CODE = env.str("BK_APP_CODE", default="bk_login")
BK_APP_SECRET = env.str("BK_APP_SECRET")
# Django SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = BK_APP_SECRET

# 蓝鲸数据库内容加密私钥
# 使用 `from cryptography.fernet import Fernet; Fernet.generate_key()` 生成随机秘钥
# 详情查看：https://cryptography.io/en/latest/fernet/
BKKRILL_ENCRYPT_SECRET_KEY = force_bytes(env.str("BKKRILL_ENCRYPT_SECRET_KEY"))
# 选择加密数据库内容的算法，可选值：SHANGMI, CLASSIC
BK_CRYPTO_TYPE = env.str("BK_CRYPTO_TYPE", "CLASSIC")
ENCRYPT_CIPHER_TYPE = "SM4CTR" if BK_CRYPTO_TYPE == "SHANGMI" else "FernetCipher"

# 蓝鲸统一的基础域和对外SCHEME
BK_DOMAIN = env.str("BK_DOMAIN", "")
BK_DOMAIN_SCHEME = env.str("BK_DOMAIN_SCHEME", default="http")
# 统一登录的外部访问地址，不包括http(s)协议
BK_LOGIN_ADDR = env.str("BK_LOGIN_ADDR", "")
BK_LOGIN_URL = f"{BK_DOMAIN_SCHEME}://{BK_LOGIN_ADDR}{SITE_URL}"
AJAX_BASE_URL = env.str("AJAX_BASE_URL", SITE_URL)
# 蓝鲸公共的Cookie的Domain(比如 bk_token和blueking_language)
BK_COOKIE_DOMAIN = "." + env.str("BK_DOMAIN")
# 登录完成后允许重定向的HOST
ALLOWED_REDIRECT_HOSTS = env.list("BK_LOGIN_ALLOWED_REDIRECT_HOSTS", default=[])

# django cookie
SESSION_COOKIE_NAME = "bklogin_sessionid"
SESSION_COOKIE_AGE = 60 * 60 * 24  # 1天
CSRF_COOKIE_NAME = "bklogin_csrftoken"
LANGUAGE_COOKIE_DOMAIN = BK_COOKIE_DOMAIN

# 登录票据
# 登录票据Cookie名称
BK_TOKEN_COOKIE_NAME = env.str("BK_LOGIN_COOKIE_NAME", default="bk_token")
# 登录票据Cookie有效期，默认1天
BK_TOKEN_COOKIE_AGE = env.int("BK_LOGIN_COOKIE_AGE", default=60 * 60 * 24)
# 登录票据校验有效期时，校验时间允许误差，防止多台机器时间不同步,默认1分钟
BK_TOKEN_OFFSET_ERROR_AGE = env.int("BK_LOGIN_COOKIE_OFFSET_ERROR_AGE", default=60)
# 无操作的失效期，默认2个小时. 长时间无操作, BkToken自动过期（Note: 调整为）
BK_TOKEN_INACTIVE_AGE = env.int("BK_TOKEN_INACTIVE_AGE", default=60 * 60 * 2)

# 用户管理相关信息
BK_USER_APP_CODE = env.str("BK_USER_APP_CODE", default="bk_user")
BK_USER_APP_SECRET = env.str("BK_USER_APP_SECRET")
BK_USER_API_URL = os.environ.get("BK_USER_API_URL", "http://bk-user")

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
    },
}
