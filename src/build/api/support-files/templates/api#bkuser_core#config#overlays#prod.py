# -*- coding: utf-8 -*-
"""
正式环境配置
"""
import urllib.parse

from bkuser_core.config.common.django_basic import *  # noqa
from bkuser_core.config.common.logging import *  # noqa
from bkuser_core.config.common.system import *  # noqa

from bkuser_global.logging import LoggingType, get_logging

DEBUG = False

# use the static root 'static' in production envs
if not DEBUG:
    STATIC_ROOT = "static"

APP_ID = "__BK_USERMGR_APP_CODE__"
APP_TOKEN = "__BK_USERMGR_APP_SECRET__"

# 数据库配置信息
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",  # 默认用mysql
        "NAME": "bk_user",
        "USER": "__BK_USERMGR_MYSQL_USER__",
        "PASSWORD": "__BK_USERMGR_MYSQL_PASSWORD__",
        "HOST": "__BK_USERMGR_MYSQL_HOST__",
        "PORT": "__BK_USERMGR_MYSQL_PORT__",
    }
}

LOGGING_DIR = "__BK_HOME__/logs/usermgr/"
LOGGING = get_logging(
    logging_type=LoggingType.FILE,
    log_level=LOG_LEVEL,
    package_name="bkuser_core",
    formatter="verbose",
    logging_dir=LOGGING_DIR,
    file_name="api",
)

# 初始化用户名、密码
SUPERUSER_USERNAME = "__BK_PAAS_ADMIN_USERNAME__"
SUPERUSER_PASSWORD = "__BK_PAAS_ADMIN_PASSWORD__"

# domain
PAAS_DOMAIN = "__BK_PAAS_PUBLIC_ADDR__"
BK_PAAS_URL = "__BK_PAAS_PUBLIC_URL__"
BK_COMPONENT_API_URL = "__BK_PAAS_PUBLIC_URL__"

# cookie访问域
BK_COOKIE_DOMAIN = ".__BK_DOMAIN__"

SECRET_KEY = "__BK_PAAS_ESB_SECRET_KEY__"

# ESB Token
ESB_TOKEN = "__BK_PAAS_APP_SECRET__"

# license
CERTIFICATE_DIR = "__BK_CERT_PATH__"
CERTIFICATE_SERVER_DOMAIN = "__BK_LICENSE_PRIVATE_ADDR__"

# redis, NOTE: NOT SUPPORT REDIS SENTINEL NOW
REDIS_MODE = "__BK_USERMGR_REDIS_MODE__"
REDIS_HOST = "__BK_USERMGR_REDIS_HOST__"
REDIS_PORT = "__BK_USERMGR_REDIS_PORT__"
REDIS_PASSWORD = "__BK_USERMGR_REDIS_PASSWORD__"
REDIS_DB = 0
REDIS_KEY_PREFIX = "bk-user-"

REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

CACHES = {
    "default": {
        "BACKEND": "bkuser_core.common.cache.DummyRedisCache",
    },
    'locmem': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'memory_cache_0',
    },
    "verification_code": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "TIMEOUT": 30 * 60,
        "KEY_PREFIX": f"{REDIS_KEY_PREFIX}verification_code",
        "VERSION": 1,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient", "PASSWORD": REDIS_PASSWORD},
        "SOCKET_CONNECT_TIMEOUT": 5,  # socket 建立连接超时设置，单位秒
        "SOCKET_TIMEOUT": 5,  # 连接建立后的读写操作超时设置，单位秒
        "IGNORE_EXCEPTIONS": True,  # redis 只作为缓存使用, 触发异常不能影响正常逻辑，可能只是稍微慢点而已
    },
}
# 全局缓存过期时间，默认为一小时
GLOBAL_CACHES_TIMEOUT = env.int("GLOBAL_CACHES_TIMEOUT", default=60 * 60)

# 快捷单元测试 dummy cache 标记
USE_DUMMY_CACHE_FOR_TEST = True

FORCE_JSONP_HEADER = "HTTP_FORCE_JSONP"
FORCE_NO_CACHE_HEADER = "HTTP_FORCE_NO_CACHE"

##########
# Celery #
##########
REDIS_URL = ""
REDIS_KEY_PREFIX = env("CACHE_REDIS_KEY_PREFIX", default="bk-user-")
CELERY_BROKER_URL = "amqp://__BK_USERMGR_RABBITMQ_USERNAME__:__BK_USERMGR_RABBITMQ_PASSWORD__@__BK_USERMGR_RABBITMQ_HOST__:__BK_USERMGR_RABBITMQ_PORT__/__BK_USERMGR_RABBITMQ_VHOST__"  # pylint: disable=line-too-long
CELERY_RESULT_BACKEND = "amqp://__BK_USERMGR_RABBITMQ_USERNAME__:__BK_USERMGR_RABBITMQ_PASSWORD__@__BK_USERMGR_RABBITMQ_HOST__:__BK_USERMGR_RABBITMQ_PORT__/__BK_USERMGR_RABBITMQ_VHOST__"  # pylint: disable=line-too-long

# ==============================================================================
# IAM
# ==============================================================================
def get_iam_config(app_id: str, app_token: str) -> dict:
    return dict(
        api_host="__BK_IAM_PRIVATE_URL__",
        system_id=env("BK_IAM_SYSTEM_ID", default="bk_usermgr"),
        # iam app 访问 url 用于回调拼接
        iam_app_host=env(
            "BK_IAM_SAAS_HOST",
            default=f"{BK_PAAS_URL}/o/{env('BK_IAM_V3_APP_CODE', default='bk_iam')}",
        ),
        apply_path="apply-custom-perm",
        # 自己的 app_id & app_token
        own_app_id=app_id,
        own_app_token=app_token,
    )


IAM_CONFIG = get_iam_config(APP_ID, APP_TOKEN)  # type: ignore
ENABLE_IAM = True

# 请求 ESB API 默认版本号
DEFAULT_BK_API_VER = "v2"

# 与 SaaS 约定的权限校验头，未传递时跳过权限校验
NEED_IAM_HEADER = "HTTP_NEED_IAM"
ACTION_ID_HEADER = "HTTP_ACTION_ID"

# ===============================================================================
# API 访问限制（暂未开启）
# ===============================================================================
INTERNAL_AUTH_TOKENS = {"TCwCnoiuUgPccj8y0Wx187vJBqzqddfLlm": {"username": "iadmin"}}
ACCESS_APP_WHITE_LIST = {"bk-iam": "lLP3gabV8M0C9vbwHQwzSYJX3WumcJsDSdVNQtq6FJVCLqJX6o"}


# ==============================================================================
# 登陆相关
# ==============================================================================
LOGIN_REDIRECT_TO = f"{BK_PAAS_URL}/login/?c_url={SITE_URL}"

# ==============================================================================
# SaaS 配置
# ==============================================================================
# SaaS 应用 Code
SAAS_CODE = "bk_user_manage"
# SaaS 请求地址，用于拼接访问地址(默认支持二进制部署)
SAAS_URL = env(
    "SAAS_URL", default=urllib.parse.urljoin(BK_PAAS_URL, f"/o/{SAAS_CODE}/")
)

# SaaS 偏好 client ip 头
CLIENT_IP_FROM_SAAS_HEADER = "HTTP_CLIENT_IP_FROM_SAAS"

# 可通过 SaaS 管理的用户目录类型
CAN_MANUAL_WRITE_LISTS = ["local"]
