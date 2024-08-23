# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import io
import logging
from functools import partialmethod
from typing import Callable

from bkuser.apps.sync.constants import SyncLogLevel

logger = logging.getLogger(__name__)


class TaskLogger:
    """任务日志记录器"""

    has_warning: bool
    _buffer: io.StringIO

    def __init__(self):
        self.has_warning = False
        self._buffer = io.StringIO()

    @property
    def logs(self):
        return self._buffer.getvalue()

    def _log(self, level: SyncLogLevel, msg: str):
        if level == SyncLogLevel.WARNING:
            self.has_warning = True

        self._buffer.write(f"{level.value} {msg}\n\n")

    # TODO (su) 支持 debug 级别的日志？但只能通过 shell 组装的 task 才能触发？
    info: Callable = partialmethod(_log, SyncLogLevel.INFO)  # type: ignore
    warning: Callable = partialmethod(_log, SyncLogLevel.WARNING)  # type: ignore
    error: Callable = partialmethod(_log, SyncLogLevel.ERROR)  # type: ignore
