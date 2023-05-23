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
from unittest.mock import patch

import pytest
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from bkuser_core.api.web.recycle_bin.views import RecycleBinCategoryBatchHardDeleteApi
from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.departments.models import Department
from bkuser_core.profiles.models import Profile
from bkuser_core.recycle_bin.constants import RecycleBinObjectType
from bkuser_core.recycle_bin.models import RecycleBin
from bkuser_core.recycle_bin.tasks import hard_delete_category_related_resource
from bkuser_core.tests.apis.utils import make_request_operator_aware
from bkuser_core.tests.utils import make_simple_department, make_simple_profile
from bkuser_core.user_settings.models import Setting

pytestmark = pytest.mark.django_db


class TestCategoryHardDelete:
    @pytest.fixture
    def default_category(self):
        category = ProfileCategory.objects.get_default()
        category.make_default_settings()
        make_simple_profile("fake_user_default")
        make_simple_department("fake_department")
        return category

    @pytest.fixture
    def test_local_category(self):
        local_category = ProfileCategory.objects.create(
            type=CategoryType.LOCAL.value, display_name="Test-Local", domain="test_local.com"
        )
        local_category.make_default_settings()
        make_simple_profile("fake_user", force_create_params={"category_id": local_category.id})
        return local_category

    @pytest.fixture
    def period_task(self, test_ldap_category):
        schedule, _ = IntervalSchedule.objects.get_or_create(every=60, period=IntervalSchedule.SECONDS)
        kwargs = json.dumps({"instance_id": test_ldap_category.id, "operator": "test"})
        create_params = {
            "interval": schedule,
            "name": f"plugin-sync-data-{test_ldap_category.id}",
            "task": "bkuser_core.categories.tasks.adapter_sync",
            "enabled": False,
            "kwargs": kwargs,
        }
        return PeriodicTask.objects.create(**create_params)

    @pytest.fixture
    def recycle_bin_relationship(self, test_ldap_category, test_local_category):
        recycle_bin_relationships: list = []
        for item in [test_ldap_category, test_local_category]:
            recycle_bin_record = RecycleBin(
                object_id=item.id, object_type=RecycleBinObjectType.CATEGORY.value, operator="test"
            )
            recycle_bin_relationships.append(recycle_bin_record)
        return RecycleBin.objects.bulk_create(recycle_bin_relationships)

    @pytest.fixture
    def hard_delete_view(self):
        return RecycleBinCategoryBatchHardDeleteApi.as_view()

    def _request_hard_delete(self, category_id, factory, hard_delete_view):
        # 硬删除， 检查所有资源是否保留
        hard_delete_url = "api/v1/web/recycle_bin/categories/hard_delete/"
        body = {"category_ids": [category_id]}
        request = factory.delete(hard_delete_url, body, format="json")
        request = make_request_operator_aware(request, "test")
        with patch("bkuser_core.recycle_bin.tasks.hard_delete_category_related_resource.delay") as _:
            response = hard_delete_view(request=request)
        return response

    def test_hard_delete_category(
        self,
        factory,
        period_task,
        hard_delete_view,
        test_ldap_category,
        test_local_category,
        default_category,
        recycle_bin_relationship,
    ):
        test_ldap_category.delete()
        assert test_ldap_category.enabled is False
        assert test_ldap_category.is_deleted

        test_local_category.delete()
        assert test_local_category.enabled is False
        assert test_local_category.is_deleted

        # 硬删除， 检查所有资源是否保留
        hard_deleted_category_ids = [test_local_category.id, test_ldap_category.id]

        for category_id in hard_deleted_category_ids:
            response = self._request_hard_delete(category_id, factory, hard_delete_view)
            assert response.status_code == 200

            hard_delete_category_related_resource(category_id=category_id)

            assert not Profile.objects.filter(category_id=category_id).exists()
            assert not Department.objects.filter(category_id=category_id).exists()
            assert not Setting.objects.filter(category_id=category_id).exists()
            assert not ProfileCategory.objects.filter(id=category_id).exists()
            assert not RecycleBin.objects.filter(
                object_type=RecycleBinObjectType.CATEGORY.value, object_id=category_id
            ).exists()
            assert not PeriodicTask.objects.filter(name=f"plugin-sync-data-{category_id}").exists()

        # 默认目录不能被删除
        response = self._request_hard_delete(default_category.id, factory, hard_delete_view)
        assert response.status_code == 200

        assert Profile.objects.filter(category_id=default_category.id).exists()
        assert Department.objects.filter(category_id=default_category.id).exists()
        assert Setting.objects.filter(category_id=default_category.id).exists()
        assert ProfileCategory.objects.filter(id=default_category.id).exists()
