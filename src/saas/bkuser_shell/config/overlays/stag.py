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
from bkuser_global.logging import LoggingType, get_logging
from bkuser_shell.config.common.django_basic import *  # noqa
from bkuser_shell.config.common.logging import *  # noqa
from bkuser_shell.config.common.platform import *  # noqa
from bkuser_shell.config.common.storage import *  # noqa
from bkuser_shell.config.common.system import *  # noqa

DEBUG = True

# ===============================================================================
# 应用运行环境配置信息
# ===============================================================================
SITE_URL = env("SITE_URL", default="/t/%s/" % APP_ID)
SITE_PREFIX = BK_PAAS_URL + SITE_URL
BUILD_STATIC = env("BK_STATIC_URL", default="%sstatic" % SITE_URL)

# ===============================================================================
# 日志设置
# ===============================================================================

LOG_LEVEL = "DEBUG"
LOGGING = get_logging(logging_type=LoggingType.STDOUT, log_level=LOG_LEVEL, package_name="bkuser_shell")
