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
import importlib
import logging
import os

from django.apps import AppConfig

logger = logging.getLogger(__name__)

PLUGINS_MODULES_PREFIX = "bkuser_core.categories.plugins."
BASE_PLUGINS_FILES_PATH = os.path.dirname(__file__) + "/plugins/"


class CategoryConfig(AppConfig):
    name = "bkuser_core.categories"

    def ready(self):

        import_plugins(BASE_PLUGINS_FILES_PATH, PLUGINS_MODULES_PREFIX)
        try:
            from . import handlers  # noqa
        except ImportError:
            # handlers 中的内容不影响正常功能流程
            pass


def import_plugins(base_file_path: str, module_prefix: str):
    for d in os.listdir(base_file_path):
        if not os.path.isdir(base_file_path + d):
            continue

        if d in ["__pycache__"]:
            continue

        module_path = module_prefix + d
        try:
            importlib.import_module(module_path)
        except Exception:  # pylint: disable=broad-except
            logger.exception("⚠️ failed to import plugin: path[%s]", module_path)
