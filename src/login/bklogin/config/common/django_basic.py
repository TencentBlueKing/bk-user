# -*- coding: utf-8 -*-
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
import os

from . import PROJECT_ROOT, env

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
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_prometheus",
    "bklogin.bkaccount",
    "bklogin.bkauth",
    "bklogin.bk_i18n",
)

MIDDLEWARE = (
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "bklogin.bkauth.middlewares.LoginMiddleware",
    "bklogin.bk_i18n.middlewares.LanguageMiddleware",
    "bklogin.bk_i18n.middlewares.ApiLanguageMiddleware",
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

# ==============================================================================
# AUTHENTICATION
# ==============================================================================
AUTH_USER_MODEL = "bkauth.User"
