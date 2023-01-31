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
from . import env
from .django_basic import MEDIA_ROOT

# paths for exempting of login
LOGIN_EXEMPT_WHITE_LIST = (
    r"/favicon.ico$",
    r"/api/v1/web/site/footer/$",
    r"/ping/$",
    r"/healthz/$",
    r"/metrics$",
    r"/api/v1/web/passwords/reset/send_email/$",
    r"/api/v1/web/passwords/reset/by_token/$",
    r"/api/v1/web/version_logs/$",
    r"/api/v1/web/passwords/settings/by_token/$",
    r"/api/v1/web/passwords/reset/verification_code/send_sms/$",
    r"/api/v1/web/passwords/reset/verification_code/verify/$",
    r"/reset_password$",
    r"/set_password$",
)

# name for bk_token in cookie
TOKEN_COOKIE_NAME = env("TOKEN_COOKIE_NAME", default="bk_token")
LOGIN_VERIFY_URI = env("LOGIN_VERIFY_URI", default="/accounts/is_login/")
LOGIN_USER_INFO_URI = env("LOGIN_USER_INFO_URI", default="/accounts/get_user/")

##############
# VersionLog #
##############
VERSION_FILE = "RELEASE.yaml"


###################
# Footer & Header #
###################
BK_DOC_URL = "https://bk.tencent.com/docs/markdown/用户管理/产品白皮书/产品简介/README.md"


# ==============================================================================
# Proxy http connections
# ==============================================================================

REQUESTS_POOL_CONNECTIONS = 20
REQUESTS_POOL_MAXSIZE = 20

# ==============================================================================
# Sentry
# ==============================================================================
SENTRY_DSN = env("SENTRY_DSN", default="")

# ==============================================================================
# OTEL
# ==============================================================================
# tracing: otel 相关配置
# if enable, default false
ENABLE_OTEL_TRACE = env.bool("BKAPP_ENABLE_OTEL_TRACE", default=False)
BKAPP_OTEL_INSTRUMENT_DB_API = env.bool("BKAPP_OTEL_INSTRUMENT_DB_API", default=False)
BKAPP_OTEL_SERVICE_NAME = env("BKAPP_OTEL_SERVICE_NAME", default="bk-user-saas")
BKAPP_OTEL_SAMPLER = env("BKAPP_OTEL_SAMPLER", default="always_on")
BKAPP_OTEL_GRPC_HOST = env("BKAPP_OTEL_GRPC_HOST", default="")
BKAPP_OTEL_DATA_TOKEN = env("BKAPP_OTEL_DATA_TOKEN", default="")
