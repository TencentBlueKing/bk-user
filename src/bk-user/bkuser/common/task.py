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
import logging

from celery import Task

logger = logging.getLogger(__name__)


class BaseTask(Task):
    """Celery 基础 Task，提供日志记录等基础功能"""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.exception("task %s(%s) failed! args: %s kwargs: %s", self.name, task_id, args, kwargs, exc_info=einfo)
        super().on_failure(exc, task_id, args, kwargs, einfo)
