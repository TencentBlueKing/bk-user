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
import json
import logging

from django_celery_beat.models import IntervalSchedule, PeriodicTask

logger = logging.getLogger(__name__)


def make_periodic_sync_task(category_id: int, interval_seconds: int):
    """创建同步周期任务"""
    try:
        schedule, _ = IntervalSchedule.objects.get_or_create(every=interval_seconds, period=IntervalSchedule.SECONDS)
    except IntervalSchedule.MultipleObjectsReturned:
        # 兼容目前已有 schedule
        schedule = IntervalSchedule.objects.filter(every=interval_seconds, period=IntervalSchedule.SECONDS)[0]

    # 通过 category_id 来做任务名
    PeriodicTask.objects.get_or_create(
        interval=schedule,
        name=str(category_id),
        task="bkuser_core.categories.tasks.adapter_sync",
        enabled=True,
        kwargs=json.dumps({"instance_id": category_id}),
    )


def update_periodic_sync_task(category_id: int, interval_seconds: int):
    """更新同步周期任务"""
    try:
        schedule, _ = IntervalSchedule.objects.get_or_create(every=interval_seconds, period=IntervalSchedule.SECONDS)
    except IntervalSchedule.MultipleObjectsReturned:
        schedule = IntervalSchedule.objects.filter(every=interval_seconds, period=IntervalSchedule.SECONDS)[0]

    # 通过 category_id 来做任务名
    try:
        p = PeriodicTask.objects.get(name=str(category_id))
        p.interval = schedule
        p.save(update_fields=["interval"])
    except PeriodicTask.DoesNotExist:
        create_params = {
            "interval": schedule,
            "name": str(category_id),
            "task": "bkuser_core.categories.tasks.adapter_sync",
            "enabled": True,
            "kwargs": json.dumps({"instance_id": category_id}),
        }
        PeriodicTask.objects.create(**create_params)


def delete_periodic_sync_task(category_id: int):
    """删除同步周期任务"""

    # 通过 category_id 来做任务名
    try:
        PeriodicTask.objects.get(name=str(category_id)).delete()
    except PeriodicTask.DoesNotExist:
        logger.warning("PeriodicTask %s has been deleted, skip it...", str(category_id))
        return
