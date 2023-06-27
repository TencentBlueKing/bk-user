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
from environ import ImproperlyConfigured

from . import env
from .django_basic import MEDIA_ROOT

# ==============================================================================
# 密码配置
# ==============================================================================

# 允许原始密码校验错误次数
RESET_PASSWORD_OLD_PASSWORD_ERROR_MAX_COUNT = 3
# 重置密码时对原始密码校验超限是否锁定
ENABLE_RESET_PASSWORD_ERROR_PROFILE_LOCK = env.bool("ENABLE_RESET_PASSWORD_ERROR_PROFILE_LOCK", default=False)

# 最大密码长度（明文）
PASSWORD_MAX_LENGTH = 32
# 重复密码最大历史数量
DEFAULT_MAX_PASSWORD_HISTORY = 3
# 用于加密密码历史
try:
    # there is a bug in django-environ, the default in bytes() is unused.
    # https://github.com/joke2k/django-environ/pull/206
    FERNET_ENCRYPT_SECRET_KEY = env.bytes("BKKRILL_ENCRYPT_SECRET_KEY")
except ImproperlyConfigured:
    FERNET_ENCRYPT_SECRET_KEY = b"hzd3Mf7eLAG4gy6N-cBZmguZ39oHprqgoOeCj3qDltg="


# ==============================================================================
# 探针配置
# ==============================================================================
COMMON_HEALTHZ_TOKEN = "56f17d8034234e92801ab59479e1259d"
HEALTHZ_PROBES: list = ["bkuser_core.monitoring.probes.DefaultDBProbe"]

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
BKAPP_OTEL_SERVICE_NAME = env("BKAPP_OTEL_SERVICE_NAME", default="bk-user-api")
BKAPP_OTEL_SAMPLER = env("BKAPP_OTEL_SAMPLER", default="always_on")
BKAPP_OTEL_GRPC_HOST = env("BKAPP_OTEL_GRPC_HOST", default="")
BKAPP_OTEL_DATA_TOKEN = env("BKAPP_OTEL_DATA_TOKEN", default="")

# ==============================================================================
# 全局应用配置
# ==============================================================================

# SaaS调用api, 传递当前登录用户(操作者), 用于鉴权
OPERATOR_HEADER = "HTTP_X_BKUSER_OPERATOR"
# 强制数据返回格式为原生格式 请求头
# 1. for_sync场景从一个用户管理同步数据到另一个用户管理中使用
FORCE_RAW_RESPONSE_HEADER = "HTTP_FORCE_RAW_RESPONSE"

# 最大的自定义字段数量（暂未启用）
# MAX_DYNAMIC_FIELDS = 20

# 默认用户 Token 的过期时间(用于发送邮件)
DEFAULT_TOKEN_EXPIRE_SECONDS = 12 * 60 * 60
# 页面临时生成用户 Token
PAGE_TOKEN_EXPIRE_SECONDS = 5 * 60

# 国际号码段默认值
DEFAULT_COUNTRY_CODE = "86"
DEFAULT_IOS_CODE = "CN"

# 大多数同步任务时间较长，保护消息队列 (没看到使用点)
# GLOBAL_MIN_SYNC_PERIOD = 60

# 是否模拟发送邮件（满足一部分系统静默需要）
FAKE_SEND_EMAIL = env.bool("FAKE_SEND_EMAIL", default=False)

# 最大分页数量
MAX_PAGE_SIZE = env.int("MAX_PAGE_SIZE", default=2000)

# 登录次数统计时间周期, 默认为一个月
LOGIN_RECORD_COUNT_SECONDS = env.int("LOGIN_RECORD_COUNT_SECONDS", default=60 * 60 * 24 * 30)

# 重置密码次数统计时间周期, 默认为十分钟
RESET_PASSWORD_RECORD_COUNT_SECONDS = env.int("RESET_PASSWORD_RECORD_COUNT_SECONDS", default=60 * 10)

# sync, 用户管理本身做业务 HTTP API 数据源, 可以被另一个用户管理同步过去
# 复用 API, 接口参数中存在 SYNC_API_PARAM 时, 以sync的接口协议返回
SYNC_API_PARAM = "for_sync"

# 通知发送时间间隔
NOTICE_INTERVAL_SECONDS = env.int("NOTICE_INTERVAL_SECONDS", default=3)

# ==============================================================================
# 黑白名单/禁用等
# ==============================================================================

# 全局开关
ENABLE_PROFILE_SENSITIVE_FILTER = env.bool("ENABLE_PROFILE_SENSITIVE_FILTER", default=False)

# profile中敏感字段, 默认接口不返回, 只有加白的app_code才允许访问
PROFILE_SENSITIVE_FIELDS = tuple(env.list("PROFILE_SENSITIVE_FIELDS", default=[]))
PROFILE_SENSITIVE_FIELDS_WHITELIST_APP_CODES = tuple(
    env.list("PROFILE_SENSITIVE_FIELDS_WHITELIST_APP_CODES", default=[])
)

# extras中的敏感字段, 以及只有白名单中的 TOKEN 请求才能获取到这批字段; 安全考虑
PROFILE_EXTRAS_SENSITIVE_FIELDS = tuple(env.list("PROFILE_EXTRAS_SENSITIVE_FIELDS", default=[]))
PROFILE_EXTRAS_SENSITIVE_FIELDS_WHITELIST_APP_CODES = tuple(
    env.list("PROFILE_EXTRAS_SENSITIVE_FIELDS_WHITELIST_APP_CODES", default=[])
)

##########
# Export #
##########
EXPORT_ORG_TEMPLATE = MEDIA_ROOT + "/excel/export_org_tmpl.xlsx"
EXPORT_LOGIN_TEMPLATE = MEDIA_ROOT + "/excel/export_login_tmpl.xlsx"

# according to https://docs.qq.com/sheet/DTktLdUtmRldob21P?tab=uty37p&c=C3A0A0
EXPORT_EXCEL_FILENAME = "bk_user_export"

# ==============================================================================
# 开发调试
# ==============================================================================
# 是否开启性能 profiling
ENABLE_PROFILING = False

# 是否使用进度条(本地开发方便)
USE_PROGRESS_BAR = False

# 是否开启ldap3 debug
ENABLE_LDAP3_DEBUG = env.bool("ENABLE_LDAP3_DEBUG", default=False)

# ==============================================================================
# 数据同步
# ==============================================================================
TASK_MAX_RETRIES = env.int("TASK_MAX_RETRIES", default=3)
RETRY_BACKOFF = env.int("RETRY_BACKOFF", default=30)


# for SaaS
# 统一使用_DATA
# DEFAULT_LOGO_URL = "img/logo_default.png"
DEFAULT_LOGO_DATA = "data:image/png;base64,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"  # noqa: E501 pylint: disable=line-too-long

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
