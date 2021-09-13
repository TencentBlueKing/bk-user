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
from bkuser_core.audit.utils import create_profile_log
from bkuser_core.profiles.constants import ProfileStatus
from bkuser_core.profiles.models import Profile
from bkuser_core.profiles.views import ProfileViewSet
from bkuser_core.tests.apis.utils import get_api_factory
from bkuser_core.tests.utils import get_one_object, make_simple_department, make_simple_profile

pytestmark = pytest.mark.django_db


class TestActionApis:
    @pytest.fixture
    def factory(self):
        return get_api_factory()

    @pytest.fixture
    def view(self):
        return ProfileViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
                "post": "restoration",
            }
        )

    # --------------- retrieve ---------------
    def test_profile_retrieve(self, factory, view):
        """测试获取用户"""
        request = factory.get("/api/v2/profiles/admin/")
        # 测试时需要手动指定 kwargs 参数当作路径参数
        response = view(request=request, lookup_value="admin")
        data = response.data
        assert data["username"] == "admin"

    def test_profile_retrieve_lookup_value(self, factory, view):
        """测试通过其他key选取用户"""
        request = factory.get("/api/v2/profiles/1/?lookup_field=id")
        # 测试时需要手动指定 kwargs 参数当作路径参数
        response = view(request=request, lookup_value="1")
        data = response.data
        assert data["username"] == "admin"

        request = factory.get("/api/v2/profiles/admin/?lookup_field=xxx")
        # 测试时需要手动指定 kwargs 参数当作路径参数
        response = view(request=request, lookup_value="admin")
        data = response.data
        assert data["username"] == "admin"

    def test_profile_retrieve_fields(self, factory, view):
        """测试获取用户"""
        request = factory.get("/api/v2/profiles/admin/?fields=username,email")
        # 测试时需要手动指定 kwargs 参数当作路径参数
        response = view(request=request, lookup_value="admin")
        data = response.data
        assert len(data.keys()) == 2
        assert data["username"] == "admin"

    def test_profile_retrieve_domain(self, factory, view):
        """测试获取用户名中是否有 domain"""
        factory = get_api_factory({"HTTP_RAW_USERNAME": False})
        make_simple_profile(
            username="adminAb",
            force_create_params={"domain": "lettest", "category_id": 2},
        )
        request = factory.get("/api/v2/profiles/adminAb@lettest/")
        # 测试时需要手动指定 kwargs 参数当作路径参数
        response = view(request=request, lookup_value="adminAb@lettest")
        assert response.data["username"] == "adminAb@lettest"

    def test_profile_retrieve_no_domain(self, factory, view):
        """测试强制用户名不返回 domain"""
        factory = get_api_factory()
        make_simple_profile(
            username="adminAb",
            force_create_params={"domain": "lettest", "category_id": 2},
        )
        request = factory.get("/api/v2/profiles/adminAb@lettest/")
        # 测试时需要手动指定 kwargs 参数当作路径参数
        response = view(request=request, lookup_value="adminAb@lettest")
        assert response.data["username"] == "adminAb"

    # --------------- update ---------------
    @pytest.mark.parametrize(
        "former_passwords,new_password,expected",
        [
            (["AAsss3@aaaa", "AAsss3@vvvv", "AAsss3@dddd"], "AAsss3@dddd", True),
            (["AAsss3@aaaa", "AAsss3@vvvv", "AAsss3@dddd"], "AAsss3@bbbb", False),
            (["AAsss3@aaaa"], "AAsss3@aaaa", True),
        ],
    )
    def test_profile_password_duplicated(self, factory, view, former_passwords, new_password, expected):
        """if new password in former passwords"""
        p = Profile.objects.get(id=1)
        for pwd in former_passwords:
            create_profile_log(p, "ResetPassword", params={"is_success": True, "password": pwd})

        request = factory.patch("/api/v2/profiles/admin/", data={"password": new_password})
        setattr(request, "operator", "faker")
        response = view(request=request, lookup_value="admin")
        if expected:
            assert response.data["code"] == "PASSWORD_DUPLICATED"
        else:
            assert response.status_code == 200

    @pytest.mark.parametrize(
        "enabled,status", [(False, ProfileStatus.NORMAL.value), (False, ProfileStatus.DELETED.value)]
    )
    def test_profile_restoration(self, factory, view, enabled, status):
        p = make_simple_profile(
            username="boouser",
            force_create_params={"category_id": 1, "enabled": enabled, "status": status},
        )
        request = factory.post(f"/api/v2/profiles/{p.username}/restoration/?include_disabled=1")
        setattr(request, "operator", "faker")
        response = view(request=request, lookup_value=f"{p.username}")
        assert response.status_code == 200
        p = get_one_object("profile", id=p.id, username=p.username)
        assert p.enabled and p.status == ProfileStatus.NORMAL.value


class TestGetDepartmentApis:
    @pytest.fixture
    def factory(self):
        return get_api_factory()

    @pytest.fixture
    def view(self):
        return ProfileViewSet.as_view({"get": "get_departments"})

    @pytest.mark.parametrize("dep_chain", [[1000, 1001, 1002], [2000, 20001]])
    def test_profile_get_department(self, factory, view, dep_chain):
        """测试通过某个用户获取组织信息"""
        factory = get_api_factory()

        target_parent = None
        for d in dep_chain:
            parent_id = target_parent if not target_parent else target_parent.pk
            target_parent = make_simple_department(str(d), force_create_params={"id": d}, parent_id=parent_id)

        p = make_simple_profile(
            username="adminAb",
            force_create_params={"domain": "lettest", "category_id": 2},
        )
        p.departments.add(target_parent)

        request = factory.get("/api/v2/profiles/adminAb@lettest/departments/")
        # 测试时需要手动指定 kwargs 参数当作路径参数
        response = view(request=request, lookup_value="adminAb@lettest")
        assert response.data[0]["name"] == target_parent.name
        assert response.data[0]["full_name"] == "/".join(str(x) for x in dep_chain)
        assert "family" not in response.data[0]

    @pytest.mark.parametrize("dep_chain", [[1000, 1001, 1002], [2000, 20001]])
    def test_profile_get_department_with_parent(self, factory, view, dep_chain):
        """测试通过某个用户获取组织信息"""
        factory = get_api_factory()

        target_parent = None
        for d in dep_chain:
            parent_id = target_parent if not target_parent else target_parent.pk
            target_parent = make_simple_department(str(d), force_create_params={"id": d}, parent_id=parent_id)

        p = make_simple_profile(
            username="adminAb",
            force_create_params={"domain": "lettest", "category_id": 2},
        )
        p.departments.add(target_parent)

        request = factory.get("/api/v2/profiles/adminAb@lettest/departments/?with_family=1")
        # 测试时需要手动指定 kwargs 参数当作路径参数
        response = view(request=request, lookup_value="adminAb@lettest")
        assert response.data[0]["name"] == target_parent.name
        assert response.data[0]["family"]

        request = factory.get("/api/v2/profiles/adminAb@lettest/departments/?with_ancestors=1")
        # 测试时需要手动指定 kwargs 参数当作路径参数
        response = view(request=request, lookup_value="adminAb@lettest")
        assert response.data[0]["name"] == target_parent.name
        assert response.data[0]["family"]
