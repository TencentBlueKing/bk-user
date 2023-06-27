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

from bkuser_core.departments.models import Department
from bkuser_core.profiles.models import Profile
from bkuser_core.user_settings.models import Setting

pytestmark = pytest.mark.django_db


class TestCategory:
    def test_delete(self, test_ldap_category, test_profile, test_department, test_setting):
        test_ldap_category.delete()

        assert test_ldap_category.enabled is False
        assert test_ldap_category.is_deleted

        assert (
            Profile.objects.filter(category_id=test_ldap_category.id, enabled=True).count()
            == Profile.objects.filter(category_id=test_ldap_category.id).count()
        )
        assert (
            Profile.objects.filter(category_id=test_ldap_category.id, status="NORMAL").count()
            == Profile.objects.filter(category_id=test_ldap_category.id).count()
        )
        assert (
            Department.objects.filter(category_id=test_ldap_category.id, enabled=True).count()
            == Department.objects.filter(category_id=test_ldap_category.id).count()
        )
        assert (
            Setting.objects.filter(category_id=test_ldap_category.id, enabled=True).count()
            == Setting.objects.filter(category_id=test_ldap_category.id).count()
        )
