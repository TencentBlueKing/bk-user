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

from bklogin.config.common.django_basic import SITE_URL
from bklogin.config.common.plugin import CUSTOM_AUTHENTICATION_BACKEND, LOGIN_TYPE

from . import env

EDITION = env.str("EDITION", default="ce")

# 用于加密登录态票据(bk_token)
BKKRILL_ENCRYPT_SECRET_KEY = env.str("ENCRYPT_SECRET_KEY")

# 与 ESB 通信的密钥
ESB_TOKEN = env.str("BK_PAAS_SECRET_KEY")

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

# external config
# license
CERTIFICATE_DIR = env.str("BK_LOGIN_LOGIN_CERT_PATH", "")
CERTIFICATE_SERVER_DOMAIN = env.str("BK_LOGIN_LOGIN_CERT_SERVER_LOCAL_ADDR", "")

# cookie名称
BK_COOKIE_NAME = "bk_token"
LANGUAGE_COOKIE_DOMAIN = BK_COOKIE_DOMAIN
# cookie 有效期，默认为1天
BK_COOKIE_AGE = env.int("BK_LOGIN_LOGIN_COOKIE_AGE", 60 * 60 * 24)
# bk_token 校验有效期校验时间允许误差，防止多台机器时间不同步,默认1分钟
BK_TOKEN_OFFSET_ERROR_TIME = env.int("BK_LOGIN_LOGIN_TOKEN_OFFSET_ERROR_TIME", 60)
# 无操作 失效期，默认2个小时. 长时间误操作, 登录态已过期
BK_INACTIVE_COOKIE_AGE = env.int("BK_LOGIN_LOGIN_INACTIVE_COOKIE_AGE", 60 * 60 * 2)


# ==============================================================================
# 企业证书校验相关
# ==============================================================================
CLIENT_CERT_FILE_PATH = os.path.join(CERTIFICATE_DIR, "platform.cert")
CLIENT_KEY_FILE_PATH = os.path.join(CERTIFICATE_DIR, "platform.key")
CERTIFICATE_SERVER_URL = f"https://{CERTIFICATE_SERVER_DOMAIN}/certificate"

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
AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS_DICT.get(
    LOGIN_TYPE, ["bklogin.bkaccount.backends.BkRemoteUserBackend"]
)
