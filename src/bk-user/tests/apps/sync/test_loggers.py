# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

import pytest
from bkuser.apps.sync.loggers import TaskLogger

pytestmark = pytest.mark.django_db


class TestTaskLogger:
    def test_logs(self):
        logger = TaskLogger()
        logger.info("start test logger")
        logger.info("this is info log")
        logger.warning("this is warning log")
        logger.error("this is error log")

        assert logger.logs == (
            "INFO start test logger\n\n"
            "INFO this is info log\n\n"
            "WARNING this is warning log\n\n"
            "ERROR this is error log\n\n"
        )

    def test_has_warning(self):
        logger = TaskLogger()
        logger.info("this is info log")
        assert not logger.has_warning

        logger.warning("this is warning log")
        assert logger.has_warning
