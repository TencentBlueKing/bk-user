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

from . import PROJECT_ROOT

# 应用密钥
SECRET_KEY = "MQtd_0cw&AiY5jT&&#w7%9sCK=HW$O_e%ch4xDd*AaP(xU0s3X"
DEBUG = True
ALLOWED_HOSTS = ["*"]

# 应用访问路径
SITE_URL = "/"
SITE_PREFIX = SITE_URL

CSRF_COOKIE_PATH = SITE_URL
CSRF_COOKIE_NAME = "bkuser_csrftoken"

# Django 3 required
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# for iframe
X_FRAME_OPTIONS = "SAMEORIGIN"

# ==============================================================================
# Middleware and apps
# ==============================================================================
MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "bkuser_shell.account.middlewares.LoginRequiredMiddleware",
    # 时区切换中间件
    "bkuser_global.middlewares.TimezoneMiddleware",
    # 静态资源服务
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # OTHER 3rd Party App
    "rest_framework",
    "drf_yasg",
    # SaaS related
    "bkuser_shell.account",
    "bkuser_shell.organization",
    "bkuser_shell.config_center",
    "bkuser_shell.categories",
    "bkuser_shell.apis",
    "bkuser_shell.version_log",
]

# ==============================================================================
# Django 项目配置
# ==============================================================================
TIME_ZONE = "Asia/Shanghai"
LANGUAGE_CODE = "zh-Hans"
SITE_ID = 1
USE_I18N = True
USE_L10N = True


MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")

# 国际化配置
LOCALE_PATHS = (os.path.join(PROJECT_ROOT, "locale"),)


LANGUAGES = (
    ("en", "English"),
    ("zh-hans", "简体中文"),
)

LANGUAGE_SESSION_KEY = "blueking_language"
LANGUAGE_COOKIE_NAME = "blueking_language"

ROOT_URLCONF = "bkuser_shell.urls"
# ===============================================================================
# 静态资源设置
# ===============================================================================
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, "static/"),
    os.path.join(PROJECT_ROOT, "media/"),
)
STATIC_VERSION = 0.2
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "staticfiles/")

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django.contrib.staticfiles.finders.DefaultStorageFinder",
)

# ==============================================================================
# Templates
# ==============================================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_ROOT, "templates"),
            os.path.join(PROJECT_ROOT, "static"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # the context to the templates
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
                "django.template.context_processors.csrf",
                "bkuser_shell.common.context_processors.shell",
                "django.template.context_processors.i18n",
            ],
            "debug": DEBUG,
        },
    },
]

# ==============================================================================
# session and cache
# ==============================================================================
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 默认为false,为true时SESSION_COOKIE_AGE无效
SESSION_COOKIE_PATH = SITE_URL

# ===============================================================================
# Authentication
# ===============================================================================
AUTH_USER_MODEL = "account.BkUser"
AUTHENTICATION_BACKENDS = ("bkuser_shell.account.backends.UserBackend",)


# 验证登录的cookie名
BK_COOKIE_NAME = "bk_token"
# 数据库初始化 管理员列表
INIT_SUPERUSER_NAMES = ["admin"]

# ==============================================================================
# DRF & Swagger 配置
# ==============================================================================
SWAGGER_SETTINGS = {
    "DEFAULT_AUTO_SCHEMA_CLASS": "bkuser_shell.common.swagger.ExtendedSwaggerAutoSchema",
}

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "bkuser_shell.common.exception_handler.ee_exception_response",
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S.%fZ",
    "SEARCH_PARAM": "lookup_field",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}
