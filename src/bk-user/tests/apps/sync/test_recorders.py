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
from bkuser.apps.data_source.models import DataSourceDepartment, DataSourceUser
from bkuser.apps.sync.constants import DataSourceSyncObjectType, SyncOperation
from bkuser.apps.sync.recorders import ChangeLogRecorder

pytestmark = pytest.mark.django_db


class TestChangeLogRecorder:
    def test_standard(self, full_general_data_source):
        users = list(DataSourceUser.objects.filter(data_source=full_general_data_source))
        departments = list(DataSourceDepartment.objects.filter(data_source=full_general_data_source))

        recorder = ChangeLogRecorder()
        recorder.add(operation=SyncOperation.CREATE, type=DataSourceSyncObjectType.USER, items=users)
        recorder.add(operation=SyncOperation.CREATE, type=DataSourceSyncObjectType.USER, items=users)

        recorder.add(operation=SyncOperation.CREATE, type=DataSourceSyncObjectType.DEPARTMENT, items=departments)

        assert len(recorder.get(operation=SyncOperation.CREATE, type=DataSourceSyncObjectType.USER)) == len(users) * 2
        assert recorder.get(operation=SyncOperation.CREATE, type=DataSourceSyncObjectType.DEPARTMENT) == departments
