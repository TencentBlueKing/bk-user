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
import logging

import yaml
from django.conf import settings

from bkuser_shell.version_log.models import VersionLogSet

logger = logging.getLogger(__name__)


def load_version_list(version_log_file: str) -> dict:
    with open(version_log_file, "r") as f:
        logger.debug("loading version log from file<%s>", f.name)
        version_content = yaml.load(f, Loader=yaml.FullLoader)
    return version_content


_g_version_list = load_version_list(version_log_file=settings.VERSION_FILE)


def get_version_list() -> VersionLogSet:
    """
    获取版本日志并校验
    """
    return VersionLogSet(**_g_version_list)
