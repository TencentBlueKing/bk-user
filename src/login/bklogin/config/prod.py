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
from .default import *  # noqa
from bkuser_global.logging import LoggingType, get_logging

SITE_URL = "/login/"
LOGIN_COMPLETE_URL = f"{HTTP_SCHEMA}://{BK_LOGIN_PUBLIC_ADDR}{SITE_URL}"
LOGGING = get_logging(
    logging_type=LoggingType.STDOUT, log_level=LOG_LEVEL, package_name="bklogin", formatter="verbose"
)
