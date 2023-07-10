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

from . import PROJECT_ROOT, env

# only for django itself(internal hashes), not a specific identity
SECRET_KEY = "Zfljnbga5QYVqNpOXLwhfGQLplZHHj3FuQWdAcaqTiDrDUfsTS"

SITE_URL = "/"

CSRF_COOKIE_PATH = SITE_URL
CSRF_COOKIE_NAME = "bkuser_csrftoken"

# ==============================================================================
# Django 基本配置
# ==============================================================================
DEBUG = False
ALLOWED_HOSTS = ["*"]

ROOT_URLCONF = "bkuser_core.urls"

# Django 3 required
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


# ==============================================================================
# 应用运行环境配置信息
# ==============================================================================


MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "bkuser_global.middlewares.RequestProvider",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "bkuser_core.common.middlewares.BKLanguageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "bkuser_core.enhanced_account.middlewares.OperatorMiddleware",
    "bkuser_global.middlewares.TimezoneMiddleware",
    "bkuser_core.common.middlewares.MethodOverrideMiddleware",
    "bkuser_core.common.middlewares.DynamicResponseFormatMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

INSTALLED_APPS = [
    "drf_yasg",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "rest_framework",
    "mptt",
    "django_celery_beat",
    "django_celery_results",
    "django_prometheus",
    # core API
    "bkuser_core.apis",
    "bkuser_core.monitoring",
    "bkuser_core.profiles",
    "bkuser_core.departments",
    "bkuser_core.user_settings",
    "bkuser_core.audit",
    "bkuser_core.categories",
    "bkuser_core.bkiam",
    "bkuser_core.recycle_bin",
    # 数据库字段翻译，需要后置于需要翻译的 Django App
    "modeltranslation",
    # apigateway sdk
    "apigw_manager.apigw",
]

# ==============================================================================
# Django 时区 & 国际化配置
# ==============================================================================
# 时区
TIME_ZONE = "Asia/Shanghai"
USE_TZ = True


# 国际化
LANGUAGE_CODE = "zh-hans"
USE_I18N = True
USE_L10N = True
LANGUAGE_SESSION_KEY = "blueking_language"
LANGUAGE_COOKIE_NAME = "blueking_language"

LOCALE_PATHS = (os.path.join(PROJECT_ROOT, "locale"),)
LANGUAGES = (
    ("zh-hans", "简体中文"),
    ("en", "English"),
)

# DB 信息国际化
MODELTRANSLATION_DEFAULT_LANGUAGE = "zh-hans"
MODELTRANSLATION_LANGUAGES = ("en", "zh-hans")

# ==============================================================================
# 静态文件配置
# ==============================================================================
STATIC_ROOT = os.path.join(PROJECT_ROOT, "staticfiles")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")

# ==============================================================================
# session and cache
# ==============================================================================
# 默认为false,为true时SESSION_COOKIE_AGE无效
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# NOTE 不要改动，否则，可能会改成和其他app的一样，这样会影响登录
SESSION_COOKIE_PATH = SITE_URL

# ===============================================================================
# Template
# ===============================================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": (os.path.join(PROJECT_ROOT, "templates"),),
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# ==============================================================================
# DRF & Swagger
# ==============================================================================
REST_FRAMEWORK = {
    "SEARCH_PARAM": "lookup_field",
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S.%fZ",
    "EXCEPTION_HANDLER": "bkuser_core.common.exception_handler.custom_exception_handler",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "ORDERING_PARAM": "ordering",
}

SWAGGER_SETTINGS = {
    "VALIDATOR_URL": None,
    # remove auth for now
    "SECURITY_DEFINITIONS": {},
    "DEFAULT_AUTO_SCHEMA_CLASS": "bkuser_core.apis.swagger.AutoModelTagSchema",
}
