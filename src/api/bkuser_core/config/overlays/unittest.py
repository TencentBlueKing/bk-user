# -*- coding: utf-8 -*-
import ldap3
from bkuser_core.config.common.django_basic import *  # noqa
from bkuser_core.config.common.logging import *  # noqa
from bkuser_core.config.common.platform import *  # noqa
from bkuser_core.config.common.storage import *  # noqa
from bkuser_core.config.common.system import *  # noqa

from bkuser_global.config import get_logging_config_dict

DEBUG = True

# ===============================================================================
# 日志设置
# ===============================================================================
LOG_LEVEL = "DEBUG"
LOGGING = get_logging_config_dict(
    log_level=LOG_LEVEL,
    logging_dir=LOGGING_DIR,
    log_class=LOG_CLASS,
    file_name=APP_ID,
    package_name="bkuser_core",
)
LOGGING["loggers"]["bkuser_core"]["handlers"] = ["console"]

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

# ==============================================================================
# SaaS
# ==============================================================================
SAAS_URL = urllib.parse.urljoin(BK_PAAS_URL, f"/o/{SAAS_CODE}/")
