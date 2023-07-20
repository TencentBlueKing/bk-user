"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS
Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import base64
import os
from pathlib import Path

import environ

from bkuser_global.config import get_db_config, init_patch

# ************************************ init settings ************************************
# read config from env
env = environ.Env()
# reading .env file
environ.Env.read_env()

# do patch
init_patch()

# get project path
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT, PROJECT_MODULE_NAME = os.path.split(PROJECT_PATH)
BASE_DIR = os.path.dirname(os.path.dirname(PROJECT_PATH))

# ************************************ django basic settings ************************************
ALLOWED_HOSTS = ["*"]

# Generic Django project settings
DEBUG = env.bool("DEBUG", False)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "o7(025idh*fj@)ohujum-ilfxl^n=@d&$xz!_$$7s$8jopd5r#"

CSRF_COOKIE_NAME = "bklogin_csrftoken"
# CSRF 验证失败处理函数
CSRF_FAILURE_VIEW = "bklogin.bkauth.views.csrf_failure"

ROOT_URLCONF = "bklogin.urls"
SITE_URL = "/"

# Django 3 required
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Application definition
INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_prometheus",
    "bklogin.bkauth",
    "bklogin.bkaccount",
    "bklogin.bk_i18n",
    "bklogin.monitoring",
)

MIDDLEWARE = (
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "bkuser_global.middlewares.RequestProvider",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "bklogin.bk_i18n.middlewares.BKLanguageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "bklogin.bk_i18n.middlewares.LanguageMiddleware",
    "bklogin.bk_i18n.middlewares.TimezoneMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # django template dir
        "DIRS": (
            # 绝对路径，比如"/home/html/django_templates" or "C:/www/django/templates".
            os.path.join(PROJECT_ROOT, "bklogin/templates"),
        ),
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.csrf",
                "bklogin.common.context_processors.site_settings",
                "django.template.context_processors.i18n",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ==============================================================================
# AUTHENTICATION
# ==============================================================================
AUTH_USER_MODEL = "bkauth.User"

# ==============================================================================
# Django 项目配置
# ==============================================================================
USE_I18N = True
USE_L10N = True

# timezone
# Default time zone for localization in the UI.
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = "Asia/Shanghai"
USE_TZ = True
TIMEZONE_SESSION_KEY = "django_timezone"

# language
LANGUAGES = (
    ("en", "English"),
    ("zh-hans", "简体中文"),
)
LANGUAGE_CODE = "zh-hans"
LANGUAGE_COOKIE_NAME = "blueking_language"
LANGUAGE_COOKIE_PATH = "/"
LOCALE_PATHS = (os.path.join(PROJECT_ROOT, "locale"),)

# ===============================================================================
# 静态资源设置
# ===============================================================================
STATICFILES_DIRS = (os.path.join(PROJECT_ROOT, "static/"),)
STATIC_VERSION = "0.2.3"
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "staticfiles/")

# CSS 文件后缀名
CSS_SUFFIX = "min.css"
# JS 文件后缀名
JS_SUFFIX = "min.js"

# ************************************ storage settings ************************************
# 数据库
DATABASES = get_db_config(env, "DATABASE")

# 缓存
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 30,
        "OPTIONS": {"MAX_ENTRIES": 1000},
    }
}

# ************************************ system settings ************************************
# Sentry
SENTRY_DSN = env("SENTRY_DSN", default="")

# requests HTTP CONNECTIONS
REQUESTS_POOL_CONNECTIONS = 20
REQUESTS_POOL_MAXSIZE = 20

# ************************************ logging settings ************************************
# logging config
LOG_LEVEL = env("LOG_LEVEL", default="INFO")
LOGGING_DIR = env("LOGGING_DIR", default=Path(PROJECT_ROOT) / "logs")

# ************************************ plugin settings ************************************
# 蓝鲸登录方式：bk_login，自定义登录方式：custom_login
LOGIN_TYPE = "bk_login"
CUSTOM_LOGIN_VIEW = ""
CUSTOM_AUTHENTICATION_BACKEND = ""
try:
    custom_conf_module_path = "bklogin.ee_login.settings_login"

    custom_conf_module = __import__(custom_conf_module_path, globals(), locals(), ["*"])
    LOGIN_TYPE = getattr(custom_conf_module, "LOGIN_TYPE", "bk_login")

    CUSTOM_LOGIN_VIEW = getattr(custom_conf_module, "CUSTOM_LOGIN_VIEW", "")
    CUSTOM_AUTHENTICATION_BACKEND = getattr(custom_conf_module, "CUSTOM_AUTHENTICATION_BACKEND", "")
    # 支持自定义登录 patch 原有的所有URL 和 添加自定义 Application  START
    ROOT_URLCONF = getattr(custom_conf_module, "ROOT_URLCONF", None) or ROOT_URLCONF
    if LOGIN_TYPE == "custom_login":
        INSTALLED_APPS = tuple(  # type: ignore
            list(INSTALLED_APPS)
            + getattr(
                custom_conf_module,
                "CUSTOM_INSTALLED_APPS",
                [],
            )
        )
    # 支持自定义登录 patch 原有的所有URL 和 添加自定义 Application  END
except ImportError as e:
    print("load custom_login settings fail!", e)
    LOGIN_TYPE = "bk_login"

# ************************************ platform settings ************************************
# 用于加密登录态票据(bk_token)
BKKRILL_ENCRYPT_SECRET_KEY = env.str("ENCRYPT_SECRET_KEY")

# 与 ESB 通信的密钥
ESB_TOKEN = env.str("BK_PAAS_SECRET_KEY")

# ESB Api URL
BK_COMPONENT_API_URL = env("BK_COMPONENT_API_URL", default="")

# Login API Auth Enabled 登录是否开启了 API 认证
BK_LOGIN_API_AUTH_ENABLED = env.bool("BK_LOGIN_API_AUTH_ENABLED", default=False)

# domain
BK_LOGIN_PUBLIC_ADDR = env.str("BK_LOGIN_PUBLIC_ADDR")
# schema = http/https, default http
HTTP_SCHEMA = env.str("BK_LOGIN_HTTP_SCHEMA", "http")

# session in cookie secure
IS_SESSION_COOKIE_SECURE = env.bool("IS_SESSION_COOKIE_SECURE", False)
if HTTP_SCHEMA == "https" and IS_SESSION_COOKIE_SECURE:
    SESSION_COOKIE_SECURE = True

# cookie访问域
BK_COOKIE_DOMAIN = "." + env.str("BK_DOMAIN")

# 用户管理API访问地址
BK_USERMGR_API_URL = env.str("BK_USERMGR_API_URL", "http://bkuserapi-web")
BK_USERMGR_SAAS_URL = env.str("BK_USERMGR_SAAS_URL", "http://bkusersaas-web")

# cookie名称
BK_COOKIE_NAME = "bk_token"
LANGUAGE_COOKIE_DOMAIN = BK_COOKIE_DOMAIN
# cookie 有效期，默认为1天
BK_COOKIE_AGE = env.int("BK_LOGIN_LOGIN_COOKIE_AGE", 60 * 60 * 24)
# bk_token 校验有效期校验时间允许误差，防止多台机器时间不同步,默认1分钟
BK_TOKEN_OFFSET_ERROR_TIME = env.int("BK_LOGIN_LOGIN_TOKEN_OFFSET_ERROR_TIME", 60)
# 无操作 失效期，默认2个小时. 长时间误操作, 登录态已过期
BK_INACTIVE_COOKIE_AGE = env.int("BK_LOGIN_LOGIN_INACTIVE_COOKIE_AGE", 60 * 60 * 2)

# ===============================================================================
# AUTHENTICATION
# ===============================================================================
LOGIN_URL = SITE_URL

LOGOUT_URL = "%slogout/" % SITE_URL

LOGIN_COMPLETE_URL = f"{HTTP_SCHEMA}://{BK_LOGIN_PUBLIC_ADDR}{SITE_URL}"

AUTHENTICATION_BACKENDS_DICT = {
    "bk_login": ["bklogin.backends.bk.BkUserBackend"],
    "custom_login": [CUSTOM_AUTHENTICATION_BACKEND],
}
AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS_DICT.get(LOGIN_TYPE, ["bklogin.backends.bk.BkUserBackend"])

# ==============================================================================
# RSA
# ==============================================================================
ENABLE_PASSWORD_RSA_ENCRYPTED = env.bool("ENABLE_PASSWORD_RSA_ENCRYPTED", False)
PASSWORD_RSA_PUBLIC_KEY = env.str("BK_PASSWORD_RSA_PUBLIC_KEY", "")
PASSWORD_RSA_PRIVATE_KEY = env.str("BK_PASSWORD_RSA_PRIVATE_KEY", "")

if ENABLE_PASSWORD_RSA_ENCRYPTED:
    print("password rsa encrypted is enabled")
    try:
        PASSWORD_RSA_PUBLIC_KEY = base64.b64decode(PASSWORD_RSA_PUBLIC_KEY).decode()
        PASSWORD_RSA_PRIVATE_KEY = base64.b64decode(PASSWORD_RSA_PRIVATE_KEY).decode()
    except Exception as e:
        rsa_key_info = (
            f"PASSWORD_RSA_PUBLIC_KEY={PASSWORD_RSA_PUBLIC_KEY},PASSWORD_RSA_PRIVATE_KEY={PASSWORD_RSA_PRIVATE_KEY}"
        )
        message = f"password rsa encrypted is enabled, but b64decode fail, {rsa_key_info}"
        print(message)
        raise e


# ==============================================================================
# IAM: SaaS Access Control
# ==============================================================================
BK_APP_CODE = env.str("BK_APP_CODE", "bk_login")
BK_APP_SECRET = env.str("BK_APP_SECRET", "")
ENABLE_IAM = env.bool("ENABLE_IAM", default=False)
BK_SYSTEM_ID_IN_IAM = env.str("BK_SYSTEM_ID_IN_IAM", BK_APP_CODE)
BK_REQUIRED_ACCESS_CONTROLLED_APPS = env.dict("BK_REQUIRED_ACCESS_CONTROLLED_APPS", default={})
BK_API_URL_TMPL = env("BK_API_URL_TMPL", default="")
BK_ACCESS_APP_DENIED_CONTACTS = env.list("BK_ACCESS_APP_DENIED_CONTACTS", default=[])
