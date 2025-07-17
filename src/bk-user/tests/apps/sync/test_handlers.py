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
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.sync.constants import DataSourceSyncPeriodType
from bkuser.apps.sync.handlers import (
    gen_data_source_sync_periodic_task_name_with_time,
    set_data_source_sync_periodic_task,
)
from bkuser.apps.sync.names import gen_data_source_sync_periodic_task_name
from django.db.models.signals import post_save
from django_celery_beat.models import PeriodicTask

pytestmark = pytest.mark.django_db


@pytest.fixture
def _enable_signal():
    post_save.connect(set_data_source_sync_periodic_task, sender=DataSource)
    yield
    post_save.disconnect(set_data_source_sync_periodic_task, sender=DataSource)


@pytest.mark.usefixtures("_enable_signal")
def test_set_data_source_sync_periodic_task_with_local(bare_local_data_source):
    """本地数据源，不会创建周期任务"""
    task_name = gen_data_source_sync_periodic_task_name(bare_local_data_source.id)
    assert not PeriodicTask.objects.filter(name=task_name).exists()


@pytest.mark.usefixtures("_enable_signal")
def test_set_data_source_sync_periodic_task_with_general_by_minute(bare_general_data_source):
    """通用 HTTP 数据源，创建任务并更新，最后删除"""
    task_name = gen_data_source_sync_periodic_task_name(bare_general_data_source.id)
    task = PeriodicTask.objects.get(name=task_name)
    assert task.interval.every == 60  # noqa: PLR2004

    bare_general_data_source.sync_config = {"period_type": DataSourceSyncPeriodType.MINUTE, "period_value": 30}  # noqa: PLR2004
    bare_general_data_source.save()
    task = PeriodicTask.objects.get(name=task_name)
    assert task.interval.every == 30  # noqa: PLR2004

    bare_general_data_source.sync_config = {}
    bare_general_data_source.save()
    assert not PeriodicTask.objects.filter(name=task_name).exists()


@pytest.mark.usefixtures("_enable_signal")
def test_set_data_source_sync_periodic_task_with_general_by_hour(bare_general_data_source):
    """通用 HTTP 数据源，创建任务并更新，最后删除"""
    task_name = gen_data_source_sync_periodic_task_name(bare_general_data_source.id)

    bare_general_data_source.sync_config = {
        "period_type": DataSourceSyncPeriodType.HOUR,
        "period_value": 1,
        "exec_times": ["2025-06-12 12:30:00+08:00"],
    }
    bare_general_data_source.save()
    task = PeriodicTask.objects.get(name=task_name)
    assert task.crontab.hour == "*"
    assert task.crontab.minute == "30"
    assert task.crontab.day_of_month == "*"
    assert task.crontab.month_of_year == "*"
    assert task.crontab.day_of_week == "*"

    bare_general_data_source.sync_config = {}
    bare_general_data_source.save()
    assert not PeriodicTask.objects.filter(name=task_name).exists()


@pytest.mark.usefixtures("_enable_signal")
def test_set_data_source_sync_periodic_task_with_general_by_day(bare_general_data_source):
    """通用 HTTP 数据源，创建任务并更新，最后删除"""
    task_name = gen_data_source_sync_periodic_task_name(bare_general_data_source.id)
    task = PeriodicTask.objects.get(name=task_name)
    assert task.interval.every == 60  # noqa: PLR2004

    bare_general_data_source.sync_config = {
        "period_type": DataSourceSyncPeriodType.DAY,
        "period_value": 30,
        "exec_times": ["2025-06-12 12:30:00+08:00", "2025-06-12 14:30:00+08:00"],
    }
    bare_general_data_source.save()
    task_name_1 = gen_data_source_sync_periodic_task_name_with_time(bare_general_data_source.id, "time_1")
    task_1 = PeriodicTask.objects.get(name=task_name_1)
    task_name_2 = gen_data_source_sync_periodic_task_name_with_time(bare_general_data_source.id, "time_2")
    task_2 = PeriodicTask.objects.get(name=task_name_2)

    assert task_1.crontab.hour == "12"
    assert task_1.crontab.minute == "30"
    assert task_2.crontab.hour == "14"
    assert task_2.crontab.minute == "30"

    bare_general_data_source.sync_config = {}
    bare_general_data_source.save()
    assert not PeriodicTask.objects.filter(name__startswith=task_name).exists()
