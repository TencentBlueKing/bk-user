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

import environ

env = environ.Env()

# Generic Django project settings
DEBUG = env.bool("DEBUG", False)

# use the static root 'static' in production envs
if not DEBUG:
    STATIC_ROOT = "static"

# 数据库配置信息
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.str("DATABASE_NAME", "bk_login"),
        "USER": env.str("DATABASE_USER"),
        "PASSWORD": env.str("DATABASE_PASSWORD"),
        "HOST": env.str("DATABASE_HOST", ""),
        "PORT": env.int("DATABASE_PORT"),
    }
}

# django secret key，同时用于加密登录态票据(bk_token)
SECRET_KEY = env.str("ENCRYPT_SECRET_KEY")
# 与 ESB 通信的密钥
ESB_TOKEN = env.str("BK_PAAS_SECRET_KEY")

# website
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
BK_USERMGR_API_URL = env.str("BK_USERMGR_API_URL", "http://bk-usermgr-svc")

# external config
# license
CERTIFICATE_DIR = env.str("BK_LOGIN_LOGIN_CERT_PATH", "")
CERTIFICATE_SERVER_DOMAIN = env.str("BK_LOGIN_LOGIN_CERT_SERVER_LOCAL_ADDR", "")


# cookie 有效期，默认为1天
BK_COOKIE_AGE = env.int("BK_LOGIN_LOGIN_COOKIE_AGE", 60 * 60 * 24)
# bk_token 校验有效期校验时间允许误差，防止多台机器时间不同步,默认1分钟
BK_TOKEN_OFFSET_ERROR_TIME = env.int("BK_LOGIN_LOGIN_TOKEN_OFFSET_ERROR_TIME", 60)
# 无操作 失效期，默认2个小时. 长时间误操作, 登录态已过期
BK_INACTIVE_COOKIE_AGE = env.int("BK_LOGIN_LOGIN_INACTIVE_COOKIE_AGE", 60 * 60 * 2)
