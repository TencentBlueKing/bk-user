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
from typing import TYPE_CHECKING, Dict, Optional
from uuid import UUID

from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from bkuser_core.categories.constants import TIMEOUT_THRESHOLD, SyncStep, SyncTaskStatus, SyncTaskType
from bkuser_core.categories.exceptions import ExistsSyncingTaskError

if TYPE_CHECKING:
    from bkuser_core.categories.models import ProfileCategory, SyncProgress, SyncTask

logger = logging.getLogger(__name__)


class ProfileCategoryManager(models.Manager):
    def switch_default(self, name):
        """切换默认用户目录"""
        category = self.get(default=True)

        if category.name == name:
            return

        category.default = False
        category.save(update_fields=["default"])

        new_default_category = self.get(name=name)
        new_default_category.default = True
        new_default_category.save(update_fields=["default"])

    def get_default(self):
        return self.get(default=True)

    def check_writable(self, category_id) -> bool:
        try:
            return self.get(pk=category_id).type in settings.CAN_MANUAL_WRITE_LISTS
        except Exception:  # pylint: disable=broad-except
            logger.exception("cannot get category<%s>", category_id)
            return False

    def get_max_order(self) -> int:
        orders = self.all().values_list("order", flat=True)
        # 若没有子组织，则返回 1
        if not orders:
            orders = [
                1,
            ]

        return max(orders)


class SyncTaskManager(models.Manager):
    def register_task(
        self, category: "ProfileCategory", operator: str, type_: SyncTaskType = SyncTaskType.MANUAL
    ) -> "SyncTask":
        qs = self.filter(category=category, status=SyncTaskStatus.RUNNING.value).order_by("-create_time")
        running = qs.first()
        if not running:
            instance = self.create(
                category=category, status=SyncTaskStatus.RUNNING.value, type=type_.value, operator=operator
            )
            return instance

        # 防御逻辑, 避免 celery 异常后, 一直无法重试.
        delta = now() - running.create_time
        if delta > TIMEOUT_THRESHOLD:
            qs.update(status=SyncTaskStatus.FAILED.value)
            return self.register_task(category=category, operator=operator, type_=type_)

        # TODO: x seconds to x hours y miniutes z seconds
        timeout = int((TIMEOUT_THRESHOLD - delta).total_seconds())
        raise ExistsSyncingTaskError(_("当前目录处于同步状态, 请在 {timeout}s 后重试.").format(timeout=timeout))

    def get_crontab_retrying_task(self, category: "ProfileCategory") -> Optional["SyncTask"]:
        qs = self.filter(
            category=category, status=SyncTaskStatus.RETRYING.value, type=SyncTaskType.AUTO.value
        ).order_by("-create_time")
        return qs.first()


class SyncProgressManager(models.Manager):
    def init_progresses(self, category: "ProfileCategory", task_id: UUID) -> Dict[SyncStep, "SyncProgress"]:
        progresses: Dict[SyncStep, "SyncProgress"] = {}

        from bkuser_core.categories.models import SyncProgressLog

        for step in [
            SyncStep.DEPARTMENTS,
            SyncStep.USERS,
            SyncStep.DEPT_USER_RELATIONSHIP,
            SyncStep.USERS_RELATIONSHIP,
        ]:
            progresses[step], created = self.get_or_create(category=category, step=step.value, task_id=task_id)
            if created:
                SyncProgressLog.objects.create(progress=progresses[step])
        return progresses
