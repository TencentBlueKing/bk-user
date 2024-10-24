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
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

import pytest
from bkuser.apps.sync.constants import SyncTaskStatus
from bkuser.apps.sync.runners import TenantSyncTaskRunner
from bkuser.apps.tenant.models import TenantDepartment, TenantUser

pytestmark = pytest.mark.django_db


class TestTenantSyncRunner:
    def test_standard(self, full_local_data_source, tenant_sync_task):
        TenantSyncTaskRunner(tenant_sync_task).run()

        tenant_sync_task.refresh_from_db()
        assert tenant_sync_task.status == SyncTaskStatus.SUCCESS

        assert TenantDepartment.objects.filter(data_source=full_local_data_source).count() == 9
        assert TenantUser.objects.filter(data_source=full_local_data_source).count() == 11
