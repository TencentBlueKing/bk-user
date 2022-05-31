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
    r"/reset_password$",
    r"/set_password$",
    r"/api/v1/password/reset/$",
    r"/api/v1/password/reset_by_token/$",
    r"api/footer/$",
    r"/metrics$",
    r"/api/v2/version_logs_list/$",
    r"/healthz/$",
    r"/ping/$",
)

# name for bk_token in cookie
TOKEN_COOKIE_NAME = env("TOKEN_COOKIE_NAME", default="bk_token")
LOGIN_VERIFY_URI = env("LOGIN_VERIFY_URI", default="/accounts/is_login/")
LOGIN_USER_INFO_URI = env("LOGIN_USER_INFO_URI", default="/accounts/get_user/")

# put on s3 maybe better
DEFAULT_LOGO_URL = "img/logo_default.png"

##########
# Export #
##########
EXPORT_ORG_TEMPLATE = MEDIA_ROOT + "/excel/export_org_tmpl.xlsx"
EXPORT_LOGIN_TEMPLATE = MEDIA_ROOT + "/excel/export_login_tmpl.xlsx"

# according to https://docs.qq.com/sheet/DTktLdUtmRldob21P?tab=uty37p&c=C3A0A0
EXPORT_EXCEL_FILENAME = "bk_user_export"

##############
# VersionLog #
##############
VERSION_FILE = "RELEASE.yaml"


###################
# Footer & Header #
###################
BK_DOC_URL = "https://bk.tencent.com/docs/markdown/用户管理/产品白皮书/产品简介/README.md"

FOOTER_CONFIG = {
    "footer": [
        {
            "text": "技术支持",
            "text_en": "Support",
            "link": "https://wpa1.qq.com/KziXGWJs?_type=wpa&qidian=true",
            "is_blank": False,
        },
        {
            "text": "社区论坛",
            "text_en": "Forum",
            "link": "https://bk.tencent.com/s-mart/community/",
            "is_blank": True,
        },
        {
            "text": "蓝鲸官网",
            "text_en": "Official",
            "link": "https://bk.tencent.com/",
            "is_blank": True,
        },
    ]
}

#############
# DRF-Crown #
#############
DRF_CROWN_RESP_CLS = "bkuser_shell.common.response.Response"
DRF_CROWN_DEFAULT_CONFIG = {"remain_request": True}

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
BKAPP_OTEL_INSTRUMENT_DB_API = env.bool("BKAPP_OTEL_INSTRUMENT_DB_API", default=True)
BKAPP_OTEL_SERVICE_NAME = env("BKAPP_OTEL_SERVICE_NAME", default="bk-user")
BKAPP_OTEL_SAMPLER = env("BKAPP_OTEL_SAMPLER", "parentbased_always_off")
BKAPP_OTEL_BK_DATA_ID = env.int("BKAPP_OTEL_BK_DATA_ID", default=-1)
BKAPP_OTEL_GRPC_HOST = env("BKAPP_OTEL_GRPC_HOST")
