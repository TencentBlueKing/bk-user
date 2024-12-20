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
from bkuser.apps.sync.handlers import set_data_source_sync_periodic_task
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
def test_set_data_source_sync_periodic_task_with_general(bare_general_data_source):
    """通用 HTTP 数据源，创建任务并更新，最后删除"""
    task_name = gen_data_source_sync_periodic_task_name(bare_general_data_source.id)
    task = PeriodicTask.objects.get(name=task_name)
    assert task.interval.every == 60  # noqa: PLR2004

    bare_general_data_source.sync_config = {"sync_period": 30}  # noqa: PLR2004
    bare_general_data_source.save()
    task = PeriodicTask.objects.get(name=task_name)
    assert task.interval.every == 30  # noqa: PLR2004

    bare_general_data_source.sync_config = {}
    bare_general_data_source.save()
    assert not PeriodicTask.objects.filter(name=task_name).exists()
