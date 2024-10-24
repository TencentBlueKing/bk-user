# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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

import pytest
from bkuser.apps.sync.constants import SyncTaskStatus
from bkuser.apps.sync.tasks import sync_data_source
from bkuser.apps.sync.workbook_temp_store import WorkbookTempStore

pytestmark = pytest.mark.django_db


class TestSyncDataSource:
    def test_success(self, data_source_sync_task, user_workbook):
        task_id = data_source_sync_task.id
        storage = WorkbookTempStore()
        temporary_storage_id = storage.save(user_workbook)

        plugin_init_extra_kwargs = {"temporary_storage_id": temporary_storage_id}
        sync_data_source(task_id, plugin_init_extra_kwargs)

        data_source_sync_task.refresh_from_db()
        assert data_source_sync_task.status == SyncTaskStatus.SUCCESS

    def test_file_not_found(self, data_source_sync_task):
        task_id = data_source_sync_task.id
        temporary_storage_id = "non_existing_key"

        plugin_init_extra_kwargs = {"temporary_storage_id": temporary_storage_id}
        sync_data_source(task_id, plugin_init_extra_kwargs)

        data_source_sync_task.refresh_from_db()
        assert data_source_sync_task.status == SyncTaskStatus.FAILED
        assert (
            f"data source sync task {task_id} require raw data in temporary storage, but not found"
            in data_source_sync_task.logs
        )

    def test_file_not_get(self, data_source_sync_task, user_workbook):
        task_id = data_source_sync_task.id
        storage = WorkbookTempStore()
        temporary_storage_id = storage.save(user_workbook)
        storage.pop(temporary_storage_id)

        plugin_init_extra_kwargs = {"temporary_storage_id": temporary_storage_id}
        sync_data_source(task_id, plugin_init_extra_kwargs)

        data_source_sync_task.refresh_from_db()
        assert data_source_sync_task.status == SyncTaskStatus.FAILED
        assert (
            f"data source sync task {task_id} require raw data in temporary storage, but not found"
            in data_source_sync_task.logs
        )
