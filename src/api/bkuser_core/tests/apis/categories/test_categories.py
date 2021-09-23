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
from bkuser_core.categories.constants import CategoryStatus
from bkuser_core.categories.views import CategoryViewSet
from bkuser_core.profiles.constants import ProfileStatus
from bkuser_core.tests.utils import get_one_object, make_simple_category, make_simple_department, make_simple_profile
from bkuser_core.user_settings.models import Setting

pytestmark = pytest.mark.django_db


class TestActionApis:
    @pytest.fixture(scope="class")
    def view(self):
        return CategoryViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy", "post": "restoration"}
        )

    def test_update_category(self, view):
        pass

    @pytest.mark.parametrize(
        "enabled,status", [(False, CategoryStatus.NORMAL.value), (False, CategoryStatus.INACTIVE.value)]
    )
    def test_category_restoration(self, factory, view, enabled, status):
        cc = make_simple_category("xoodomain", "Domain", force_create_params={"enabled": enabled, "status": status})
        setting_id = []
        for setting in cc.make_default_settings():
            setting.enabled = 0
            setting.save(update_fields=["enabled"])
            setting_id.append(setting.id)
        d = make_simple_department("dep", parent_id=1, force_create_params={"category_id": cc.id, "enabled": enabled})
        p = make_simple_profile("profile", force_create_params={"category_id": cc.id, "enabled": enabled})
        request = factory.post(f"/api/v2/categories/{cc.id}/restoration/?include_disabled=1")
        setattr(request, "operator", "faker")
        response = view(request=request, lookup_value=f"{cc.id}")
        assert response.status_code == 200
        cc = get_one_object("profilecategory", id=cc.id, domain=cc.domain)
        assert cc.enabled and cc.status == CategoryStatus.NORMAL.value
        assert get_one_object("department", id=d.id, name=d.name).enabled
        p = get_one_object("profile", id=p.id, username=p.username)
        assert p.enabled and p.status == ProfileStatus.NORMAL.value
        assert {x.id for x in Setting.objects.filter(id__in=setting_id, enabled=True)} == set(setting_id)


class TestListCreateApis:
    @pytest.fixture(scope="class")
    def view(self):
        return CategoryViewSet.as_view({"get": "list", "post": "create"})

    @pytest.mark.parametrize(
        "all_count,fields,result_count,include_disabled,expected_fields",
        [
            (10, "id,display_name,domain,enabled", 5, "false", "id,display_name,domain,enabled"),
            (10, "id,display_name,domain", 10, "true", "id,display_name,domain,enabled"),
            (10, "id,display_name,domain,enabled", 10, "true", "id,display_name,domain,enabled"),
        ],
    )
    def test_category_include_enabled_fields(
        self, factory, view, all_count, fields, result_count, include_disabled, expected_fields
    ):
        """测试目录软删除显式拉取和字段选择"""
        for i in range(1, all_count):
            make_simple_category(f"domain{i}", f"Display{i}", force_create_params={"enabled": i % 2 == 0})
        response = view(
            request=factory.get(f"/api/v2/categories/?fields={fields}&include_disabled={include_disabled}")
        )
        assert response.data["count"] == result_count
        assert set(response.data["results"][0].keys()) == set(expected_fields.split(","))
