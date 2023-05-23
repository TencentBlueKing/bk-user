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

import pytest
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from bkuser_core.api.web.recycle_bin.views import RecycleBinBatchCategoryRevertApi
from bkuser_core.categories.constants import CategoryStatus
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.recycle_bin.constants import RecycleBinObjectType
from bkuser_core.recycle_bin.models import RecycleBin
from bkuser_core.tests.apis.utils import get_api_factory, make_request_operator_aware

pytestmark = pytest.mark.django_db


class TestCategoryRevert:
    @pytest.fixture(scope="class")
    def factory(self):
        return get_api_factory()

    @pytest.fixture
    def revert_view(self):
        return RecycleBinBatchCategoryRevertApi.as_view()

    @pytest.fixture
    def period_task(self, test_ldap_category):
        schedule, _ = IntervalSchedule.objects.get_or_create(every=60, period=IntervalSchedule.SECONDS)
        kwargs = json.dumps({"instance_id": test_ldap_category.id, "operator": "tester"})
        create_params = {
            "interval": schedule,
            "name": f"plugin-sync-data-{test_ldap_category.id}",
            "task": "bkuser_core.categories.tasks.adapter_sync",
            "enabled": False,
            "kwargs": kwargs,
        }
        task = PeriodicTask.objects.create(**create_params)
        return task

    @pytest.fixture
    def recycle_bin_relationship(self, test_ldap_category):
        relationship_kv: dict = {
            "object_id": test_ldap_category.id,
            "object_type": RecycleBinObjectType.CATEGORY.value,
            "operator": "tester",
        }
        RecycleBin.objects.create(**relationship_kv)

    def test_revert(self, factory, revert_view, test_ldap_category, period_task, recycle_bin_relationship):
        # 测试用户目录删除还原，同步任务还原
        test_ldap_category.delete()
        category_id = test_ldap_category.id
        # 测试目录还原
        revert_url = "api/v1/web/recycle_bin/categories/revert/"
        body = {"category_ids": [category_id]}
        request = factory.post(revert_url, body, format="json")
        request = make_request_operator_aware(request, "test")
        response = revert_view(request=request)

        assert response.status_code == 200

        category = ProfileCategory.objects.get(id=category_id)
        task = PeriodicTask.objects.get(name=f"plugin-sync-data-{category_id}")
        assert category.enabled
        assert category.status == CategoryStatus.NORMAL.value
        assert task.enabled

        assert not RecycleBin.objects.filter(
            object_type=RecycleBinObjectType.CATEGORY.value, object_id=category.id
        ).exists()
