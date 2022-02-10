# -*- coding: utf-8 -*-
import ldap3
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
