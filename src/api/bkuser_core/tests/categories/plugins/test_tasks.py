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
import pytest

from bkuser_core.categories.constants import SyncTaskStatus, SyncTaskType
from bkuser_core.categories.models import SyncTask
from bkuser_core.categories.tasks import sync_data_task

pytestmark = pytest.mark.django_db


class TestSyncDataTask:
    @pytest.fixture
    def sync_task(self, test_ldap_category):
        return SyncTask.objects.register_task(category=test_ldap_category, operator="admin", type_=SyncTaskType.AUTO)

    @pytest.mark.parametrize(
        "retrying_status",
        [
            [True],
            [False],
            [True, False],
            [True, True, False],
            [True, True, True],
        ],
    )
    def test_sync_data_task(self, test_ldap_category, sync_task, retrying_status):
        """测试同步数据任务"""

        for t in retrying_status:
            with pytest.raises(ValueError):
                with sync_data_task(test_ldap_category, sync_task.id, t):
                    raise ValueError("Anything wrong")

        sync_task = SyncTask.objects.get(pk=sync_task.id)
        assert (
            sync_task.status == SyncTaskStatus.RETRYING.value if retrying_status[-1] else SyncTaskStatus.FAILED.value
        )

        assert sync_task.retried_count == len([x for x in retrying_status if x])
