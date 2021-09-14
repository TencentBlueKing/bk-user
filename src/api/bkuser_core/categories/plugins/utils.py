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

from bkuser_core.categories.plugins.base import TypeList, TypeProtocol
from bkuser_core.common.progress import progress
from django_celery_beat.models import IntervalSchedule, PeriodicTask

logger = logging.getLogger(__name__)


def make_periodic_sync_task(category_id: int, operator: str, interval_seconds: int):
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
        kwargs=json.dumps({"instance_id": category_id, "operator": operator}),
    )


def update_periodic_sync_task(category_id: int, operator: str, interval_seconds: int):
    """更新同步周期任务"""
    try:
        schedule, _ = IntervalSchedule.objects.get_or_create(every=interval_seconds, period=IntervalSchedule.SECONDS)
    except IntervalSchedule.MultipleObjectsReturned:
        schedule = IntervalSchedule.objects.filter(every=interval_seconds, period=IntervalSchedule.SECONDS)[0]

    # 通过 category_id 来做任务名
    kwargs = json.dumps({"instance_id": category_id, "operator": operator})
    try:
        p: PeriodicTask = PeriodicTask.objects.get(name=str(category_id))
        p.interval = schedule
        p.kwargs = kwargs
        p.save(update_fields=["interval", "kwargs"])
    except PeriodicTask.DoesNotExist:
        create_params = {
            "interval": schedule,
            "name": str(category_id),
            "task": "bkuser_core.categories.tasks.adapter_sync",
            "enabled": True,
            "kwargs": kwargs,
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


def handle_with_progress_info(
    item_list: TypeList[TypeProtocol], progress_title: str, continue_if_exception: bool = True
):
    """控制进度"""
    total = len(item_list)
    for index, (key, item) in enumerate(item_list.items()):  # type: int, (str, TypeProtocol)
        try:
            progress(
                index + 1,
                total,
                f"{progress_title}: {item.display_str}<{key}> ({index + 1}/{total})",
            )
            yield item
        except Exception:
            logger.exception("%s failed", progress_title)
            if continue_if_exception:
                continue

            raise
