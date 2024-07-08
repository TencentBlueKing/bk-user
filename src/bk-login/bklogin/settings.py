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
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

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

ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "django_prometheus",
    "bklogin.authentication",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
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
SITE_URL = env.str("SITE_URL", default="/login/")
# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR / "staticfiles"
WHITENOISE_STATIC_PREFIX = os.path.join(SITE_URL, "staticfiles/")
# STATIC_URL 也可以是CDN地址
STATIC_URL = env.str("STATIC_URL", default=SITE_URL + "staticfiles/")

# 登录服务的AppCode/AppSecret
BK_APP_CODE = env.str("BK_APP_CODE", default="bk_login")
BK_APP_SECRET = env.str("BK_APP_SECRET")
# Django SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = BK_APP_SECRET
# [兼容] 用于判断是否 ESB 请求（2.x 版本里，paas_v2/ESB/console/login 共用 bk_paas 的 AppSecret）
BK_PAAS_APP_SECRET = env.str("BK_PAAS_APP_SECRET", "")

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
BK_COOKIE_DOMAIN = f".{BK_DOMAIN}"
# 登录完成后允许重定向的HOST
# 支持匹配:
#  (1) * 匹配任意域名
#  (2) 泛域名匹配，比如 .example.com 可匹配 foo.example.com、example.com、foo.example.com:8000、example.com:8080
#  (3) 精确域名匹配，比如 example.com 可匹配 example.com、example.com:8000
#  (4) 精确域名&端口匹配，比如 example.com:9000 只可匹配 example.com:9000
# 默认蓝鲸体系域名都可以匹配
ALLOWED_REDIRECT_HOSTS = env.list("BK_LOGIN_ALLOWED_REDIRECT_HOSTS", default=[BK_COOKIE_DOMAIN])
# 语言Cookie（蓝鲸体系共享）
LANGUAGE_COOKIE_DOMAIN = BK_COOKIE_DOMAIN

# session & csrf
_BK_LOGIN_URL_PARSE_URL = urlparse(BK_LOGIN_URL)
_BK_LOGIN_HOSTNAME = _BK_LOGIN_URL_PARSE_URL.hostname  # 去除端口的域名
_BK_LOGIN_NETLOC = _BK_LOGIN_URL_PARSE_URL.netloc  # 若有端口，则会带上对应端口
_BK_LOGIN_IS_SPECIAL_PORT = _BK_LOGIN_URL_PARSE_URL.port in [None, 80, 443]
_BK_LOGIN_SCHEME = _BK_LOGIN_URL_PARSE_URL.scheme
_BK_LOGIN_URL_MD5_16BIT = hashlib.md5(BK_LOGIN_URL.encode("utf-8")).hexdigest()[8:-8]
# 注意：Cookie Domain是不支持端口的
SESSION_COOKIE_DOMAIN = _BK_LOGIN_HOSTNAME
CSRF_COOKIE_DOMAIN = SESSION_COOKIE_DOMAIN
SESSION_COOKIE_NAME = f"bklogin_sessionid_{_BK_LOGIN_URL_MD5_16BIT}"
SESSION_COOKIE_AGE = 60 * 60 * 24  # 1天
CSRF_COOKIE_NAME = f"bklogin_csrftoken_{_BK_LOGIN_URL_MD5_16BIT}"
# 对于特殊端口，带端口和不带端口都得添加，其他只需要添加默认原生的即可
CSRF_TRUSTED_ORIGINS = [_BK_LOGIN_HOSTNAME, _BK_LOGIN_NETLOC] if _BK_LOGIN_IS_SPECIAL_PORT else [_BK_LOGIN_NETLOC]

# cors
CORS_ALLOW_CREDENTIALS = True  # 在 response 添加 Access-Control-Allow-Credentials, 即允许跨域使用 cookies
CORS_ORIGIN_WHITELIST = (
    [f"{_BK_LOGIN_SCHEME}://{_BK_LOGIN_HOSTNAME}", f"{_BK_LOGIN_SCHEME}://{_BK_LOGIN_NETLOC}"]
    if _BK_LOGIN_IS_SPECIAL_PORT
    else [f"{_BK_LOGIN_SCHEME}://{_BK_LOGIN_NETLOC}"]
)
# debug/联调测试时需要允许额外的域名跨域请求
CORS_ORIGIN_ADDITIONAL_WHITELIST = env.list("CORS_ORIGIN_ADDITIONAL_WHITELIST", default=[])
CORS_ORIGIN_WHITELIST.extend(CORS_ORIGIN_ADDITIONAL_WHITELIST)

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
BK_USER_API_URL = env.str("BK_USER_API_URL", default="http://bk-user")

# bk apigw url tmpl
BK_API_URL_TMPL = env.str("BK_API_URL_TMPL", default="")

# footer / logo / title 等全局配置存储的共享仓库地址
BK_SHARED_RES_URL = env.str("BK_SHARED_RES_URL", default="")

# ------------------------------------------ 日志配置 ------------------------------------------

# 日志等级，高于或等于该等级的日志才会被记录
LOG_LEVEL = env.str("LOG_LEVEL", default="ERROR")
# 用于存放日志文件的目录，默认值为空，表示不使用任何文件，所有日志直接输出到控制台。
# 可配置为有效目录，支持相对或绝对地址，比如："logs" 或 "/var/lib/app_logs/"。
# 配置本选项后，原有的控制台日志输出将关闭。
LOGGING_DIRECTORY = env.str("LOGGING_DIRECTORY", default=None)
# 日志文件格式，可选值为：json/text
LOGGING_FILE_FORMAT = env.str("LOGGING_FILE_FORMAT", default="json")

if LOGGING_DIRECTORY is None:
    logging_to_console = True
    logging_directory = None
else:
    logging_to_console = False
    # The dir allows both absolute and relative path, when it's relative, combine
    # the value with project's base directory
    logging_directory = Path(BASE_DIR) / Path(LOGGING_DIRECTORY)
    logging_directory.mkdir(exist_ok=True)

# 是否总是打印日志到控制台，默认关闭
LOGGING_ALWAYS_CONSOLE = env.bool("LOGGING_ALWAYS_CONSOLE", default=False)
if LOGGING_ALWAYS_CONSOLE:
    logging_to_console = True


def build_logging_config(log_level: str, to_console: bool, file_directory: Optional[Path], file_format: str) -> Dict:
    """Build the global logging config dict.

    :param log_level: The log level.
    :param to_console: If True, output the logs to the console.
    :param file_directory: If the value is not None, output the logs to the given directory.
    :param file_format: The format of the logging file, "json" or "text".
    :return: The logging config dict.
    """

    def _build_file_handler(log_path: Path, filename: str, format: str) -> Dict:
        if format not in ("json", "text"):
            raise ValueError(f"Invalid file_format: {file_format}")
        formatter = "verbose_json" if format == "json" else "verbose"
        return {
            "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
            "level": log_level,
            "formatter": formatter,
            "filename": str(log_path / filename),
            # Set max file size to 100MB
            "maxBytes": 100 * 1024 * 1024,
            "backupCount": 5,
        }

    handlers_config: Dict[str, Any] = {
        "null": {"level": log_level, "class": "logging.NullHandler"},
        "console": {"level": log_level, "class": "logging.StreamHandler", "formatter": "verbose"},
    }
    # 生成指定 Logger 对应的 Handlers
    logger_handlers_map: Dict[str, List[str]] = {}
    for logger_name in ["root", "component"]:
        handlers = []

        if to_console:
            handlers.append("console")

        if file_directory:
            # 生成 logger 对应日志文件的 Handler
            handlers_config[logger_name] = _build_file_handler(
                file_directory, f"{logger_name}-{file_format}.log", file_format
            )
            handlers.append(logger_name)

        logger_handlers_map[logger_name] = handlers

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": (
                    "%(name)s %(levelname)s [%(asctime)s] %(pathname)s %(lineno)d %(funcName)s %(process)d %(thread)d "
                    "\n \t%(message)s \n"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "verbose_json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "fmt": (
                    "%(name)s %(levelname)s %(asctime)s %(pathname)s %(lineno)d "
                    "%(funcName)s %(process)d %(thread)d %(message)s"
                ),
            },
            "simple": {"format": "%(name)s %(levelname)s %(message)s"},
        },
        "handlers": handlers_config,
        # the root logger, 用于整个项目的默认 logger
        "root": {"handlers": logger_handlers_map["root"], "level": log_level, "propagate": False},
        "loggers": {
            "django": {"handlers": ["null"], "level": "INFO", "propagate": True},
            "django.server": {"handlers": logger_handlers_map["root"], "level": log_level, "propagate": False},
            "django.request": {"handlers": logger_handlers_map["root"], "level": log_level, "propagate": False},
            # 除 root 外的其他指定 Logger
            **{
                logger_name: {"handlers": handlers, "level": log_level, "propagate": False}
                for logger_name, handlers in logger_handlers_map.items()
                if logger_name != "root"
            },
        },
    }


LOGGING = build_logging_config(LOG_LEVEL, logging_to_console, logging_directory, LOGGING_FILE_FORMAT)

# ------------------------------------------ Healthz 配置 ------------------------------------------

# 调用 Healthz API 需要的 Token
HEALTHZ_TOKEN = env.str("HEALTHZ_TOKEN", "")
# 服务健康探针配置
HEALTHZ_PROBES = env.list(
    "HEALTHZ_PROBES",
    default=[
        "bklogin.monitoring.healthz.probes.MysqlProbe",
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
OTEL_SERVICE_NAME = env.str("OTEL_SERVICE_NAME", "bk-login")
# sdk 采样规则（always_on / always_off ...）
OTEL_SAMPLER = env.str("OTEL_SAMPLER", "always_on")
# OTEL 上报地址（grpc）
OTEL_GRPC_URL = env.str("OTEL_GRPC_URL", "")
# OTEL 上报到监控平台的数据 Token，可通过监控平台上新建应用获得
OTEL_DATA_TOKEN = env.str("OTEL_DATA_TOKEN", "")
# 是否记录 DB 相关 tracing
OTEL_INSTRUMENT_DB_API = env.bool("OTEL_INSTRUMENT_DB_API", False)

if ENABLE_OTEL_TRACE or SENTRY_DSN:
    INSTALLED_APPS += ("bklogin.monitoring.tracing",)

# ------------------------------------------ 蓝鲸通知中心配置 ------------------------------------------

# 通知中心的功能可通过配置开启
ENABLE_BK_NOTICE = env.bool("ENABLE_BK_NOTICE", False)
if ENABLE_BK_NOTICE:
    INSTALLED_APPS += ("bk_notice_sdk",)
    # 对接通知中心的环境，默认为生产环境
    BK_NOTICE_ENV = env.str("BK_NOTICE_ENV", "prod")
    BK_NOTICE = {
        "STAGE": BK_NOTICE_ENV,
        "LANGUAGE_COOKIE_NAME": LANGUAGE_COOKIE_NAME,
        "DEFAULT_LANGUAGE": "en",
        "PLATFORM": BK_APP_CODE,  # 平台注册的 code，用于获取系统通知消息时进行过滤
        "BK_API_URL_TMPL": BK_API_URL_TMPL,
        "BK_API_APP_CODE": BK_APP_CODE,  # 用于调用 apigw 认证
        "BK_API_SECRET_KEY": BK_APP_SECRET,  # 用于调用 apigw 认证
    }

# ------------------------------------------ 业务逻辑配置 ------------------------------------------
