# -*- coding: utf-8 -*-
import os

import ldap3

from bkuser_core.config.common import PROJECT_ROOT
from bkuser_core.config.common.django_basic import *  # noqa
from bkuser_core.config.common.logging import *  # noqa
from bkuser_core.config.common.platform import *  # noqa
from bkuser_core.config.common.storage import *  # noqa
from bkuser_core.config.common.system import *  # noqa
from bkuser_global.logging import LoggingType, get_logging

DEBUG = True

# ===============================================================================
# 日志设置
# ===============================================================================
LOG_LEVEL = "DEBUG"
LOGGING = get_logging(logging_type=LoggingType.STDOUT, log_level=LOG_LEVEL, package_name="bkuser_core")


def get_loggers(package_name: str, log_level: str) -> dict:
    return {
        "django": {
            "handlers": ["null"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["root"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["root"],
            "level": "INFO",
            "propagate": True,
        },
        "django.security": {
            "handlers": ["root"],
            "level": "INFO",
            "propagate": True,
        },
        package_name: {
            "handlers": ["root"],
            "level": log_level,
            "propagate": True,
        },
        "": {
            "handlers": ["root"],
            "level": log_level,
        },
        "requests": {
            "handlers": ["root"],
            "level": log_level,
            "propagate": True,
        },
        # 组件调用日志
        "component": {
            "handlers": ["root"],
            "level": "WARN",
            "propagate": True,
        },
        "iam": {
            "handlers": ["root"],
            "level": log_level,
            "propagate": True,
        },
    }


# patch the unittest logging loggers
LOGGING["loggers"] = get_loggers("bkuser_core", LOG_LEVEL)


# ==============================================================================
# Test Ldap
# ==============================================================================
TEST_LDAP = {
    "url": "dev.bluesspace",
    "base": "dc=example,dc=org",
    "user": "cn=admin,dc=example,dc=org",
    "password": "x0x0x0x0",
    "user_class": "inetOrgPerson",
    "organization_class": "organizationalUnit",
}

# Ldap connection mock
LDAP_CONNECTION_EXTRAS_PARAMS = {"client_strategy": ldap3.MOCK_SYNC}

# celery results backend use from env(in unittest)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")


# ==============================================================================
# Email
# ==============================================================================
FAKE_SEND_EMAIL = True


# ==============================================================================
# 全局应用配置
# ==============================================================================
# 进度条是否刷新缓冲区（历史打印是否保存）
FLUSH_PROGRESS_BAR = False

# ==============================================================================
# profiling
# ==============================================================================
ENABLE_PROFILING = False
