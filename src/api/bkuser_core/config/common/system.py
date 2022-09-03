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

# ==============================================================================
# 密码配置
# ==============================================================================

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

# 强制数据返回格式为原生格式 请求头
#### 1. SaaS调用api
#### 2. for_sync场景从一个用户管理同步数据到另一个用户管理中使用
FORCE_RAW_RESPONSE_HEADER = "HTTP_FORCE_RAW_RESPONSE"
# 强制返回原始用户名（不带登陆域）请求头
FORCE_RAW_USERNAME_HEADER = "HTTP_RAW_USERNAME"
OPERATOR_HEADER = "HTTP_X_BKUSER_OPERATOR"

# 最大的自定义字段数量（暂未启用）
MAX_DYNAMIC_FIELDS = 20

# 默认用户 Token 的过期时间(用于发送邮件)
DEFAULT_TOKEN_EXPIRE_SECONDS = 12 * 60 * 60
# 页面临时生成用户 Token
PAGE_TOKEN_EXPIRE_SECONDS = 5 * 60

# 国际号码段默认值
DEFAULT_COUNTRY_CODE = "86"
DEFAULT_IOS_CODE = "CN"

# 大多数同步任务时间较长，保护消息队列
GLOBAL_MIN_SYNC_PERIOD = 60

# 是否模拟发送邮件（满足一部分系统静默需要）
FAKE_SEND_EMAIL = env.bool("FAKE_SEND_EMAIL", default=False)

# 最大分页数量
MAX_PAGE_SIZE = env.int("MAX_PAGE_SIZE", default=2000)

# 登录次数统计时间周期, 默认为一个月
LOGIN_RECORD_COUNT_SECONDS = env.int("LOGIN_RECORD_COUNT_SECONDS", default=60 * 60 * 24 * 30)

DRF_CROWN_DEFAULT_CONFIG = {"remain_request": True}

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
