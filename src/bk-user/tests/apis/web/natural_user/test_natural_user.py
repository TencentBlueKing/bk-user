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
from typing import Dict, List

import pytest
from bkuser.apps.data_source.models import DataSourceDepartmentUserRelation, DataSourceUserLeaderRelation
from bkuser.apps.natural_user.models import DataSourceUserNaturalUserRelation
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


class TestNaturalUserTenantUserListApi:
    def test_list_bound_natural_user(
        self, api_client, bk_user, natural_user, default_data_source, tenant_users, random_tenant_users, default_tenant
    ):
        """
        绑定自然人的情况
        """

        resp = api_client.get(reverse("person_center.current_natural_user"))
        assert resp.status_code == status.HTTP_200_OK

        assert natural_user.id == resp.data["id"]
        assert natural_user.full_name == resp.data["full_name"]

        # 应该返回自然人所绑定数据源用户的所有租户用户
        data_source_user_ids = DataSourceUserNaturalUserRelation.objects.filter(natural_user=natural_user).values_list(
            "data_source_user_id", flat=True
        )
        tenant_users_from_db = TenantUser.objects.filter(data_source_user__in=data_source_user_ids)
        assert tenant_users_from_db.count() == len(resp.data["tenant_users"])

        # 当前的登录账号，置顶
        assert bk_user.get_property("bk_username") == resp.data["tenant_users"][0]["id"]

        tenant_user_map = {user.id: user for user in tenant_users_from_db}
        for item in resp.data["tenant_users"]:
            assert item["id"] in tenant_user_map

            tenant_user: TenantUser = tenant_user_map[item["id"]]
            data_source_user = tenant_user.data_source_user
            assert item["username"] == data_source_user.username
            assert item["full_name"] == data_source_user.full_name

            assert item["tenant"]["id"] == tenant_user.tenant_id
            assert item["tenant"]["name"] == tenant_user.tenant.name

    def test_list_not_bound_natural_user(
        self, api_client, bk_user, tenant_users, random_tenant_users, default_tenant, default_data_source
    ):
        """
        未绑定自然人的情况
        """

        resp = api_client.get(reverse("person_center.current_natural_user"))
        assert resp.status_code == status.HTTP_200_OK

        # 未绑定自然人，返回的自然人信息为当前登录租户用户的ID和full_name
        current_tenant_user = TenantUser.objects.get(id=bk_user.get_property("bk_username"))
        assert current_tenant_user.id == resp.data["id"]
        assert current_tenant_user.data_source_user.full_name == resp.data["full_name"]

        # 返回当前租户用户所属数据源用户的所有关联租户用户
        tenant_users = TenantUser.objects.filter(data_source_user_id=current_tenant_user.data_source_user_id)
        assert len(resp.data["tenant_users"]) == tenant_users.count()

        # 当前的登录账号，置顶
        assert resp.data["tenant_users"][0]["id"] == current_tenant_user.id


class TestNaturalUserTenantUserRetrieveApi:
    def _check_departments_is_exist(self, tenant_user: TenantUser, checked_departments: List[Dict]):
        """
        检查返回的租户部门数据是否真实
        """
        data_source_user = tenant_user.data_source_user
        # 所属部门
        tenant_departments_from_db = TenantDepartment.objects.filter(
            data_source_department_id__in=DataSourceDepartmentUserRelation.objects.filter(
                user=data_source_user
            ).values_list("department_id", flat=True),
            tenant_id=tenant_user.tenant_id,
        ).values("id", "data_source_department__name")
        tenant_department_map = {
            item["id"]: item["data_source_department__name"] for item in tenant_departments_from_db
        }

        for department in checked_departments:
            assert department["id"] in tenant_department_map
            assert department["name"] == tenant_department_map[department["id"]]

    def _check_leaders_is_exist(self, tenant_user: TenantUser, checked_leaders: List[Dict]):
        """
        检查返回的租户上级用户数据是否真实
        """
        data_source_user = tenant_user.data_source_user
        # 上级
        data_source_leader_ids = DataSourceUserLeaderRelation.objects.filter(user=data_source_user).values_list(
            "leader_id", flat=True
        )
        tenant_leaders_from_db = TenantUser.objects.filter(
            data_source_user_id__in=data_source_leader_ids, tenant_id=tenant_user.tenant_id
        ).values("id", "data_source_user__username", "data_source_user__full_name")
        tenant_leader_map = {leader["id"]: leader for leader in tenant_leaders_from_db}
        for user in checked_leaders:
            assert user["id"] in tenant_leader_map
            leader_info = tenant_leader_map[user["id"]]
            assert user["username"] in leader_info["data_source_user__username"]
            assert user["full_name"] in leader_info["data_source_user__full_name"]

    def _check_property(self, tenant_user: TenantUser, general_property: Dict):
        """
        检查返回的租户用户常规数据，是否真实
        """
        data_source_user = tenant_user.data_source_user

        assert general_property["username"] == data_source_user.username
        assert general_property["full_name"] == data_source_user.full_name
        assert general_property["email"] == data_source_user.email
        assert general_property["phone"] == data_source_user.phone
        assert general_property["phone_country_code"] == data_source_user.phone_country_code

        assert general_property["is_inherited_phone"] == tenant_user.is_inherited_phone
        assert general_property["custom_phone"] == tenant_user.custom_phone
        assert general_property["custom_phone_country_code"] == tenant_user.custom_phone_country_code

        assert general_property["is_inherited_email"] == tenant_user.is_inherited_email
        assert general_property["custom_email"] == tenant_user.custom_email

    def test_retrieve_tenant_user_with_bound_natural_user(
        self,
        api_client,
        natural_user,
        tenant_users,
        tenant_departments,
        random_tenant_users,
        random_tenant_departments,
    ):
        """
        绑定自然人情况下，可以随机访问
        """
        for user in [*tenant_users, *random_tenant_users]:
            resp = api_client.get(reverse("person_center.tenant_users.retrieve", kwargs={"id": user.id}))
            assert resp.status_code == status.HTTP_200_OK
            # 常规属性检查
            self._check_property(user, resp.data)
            # 上级检查
            self._check_leaders_is_exist(user, resp.data["leaders"])
            # 归属部门检查
            self._check_departments_is_exist(user, resp.data["departments"])

    def test_retrieve_additional_tenant_user_without_natural_user(self, api_client, additional_tenant_user):
        """
        未捆绑自然人情况下，测试和当前用户非同一数据源用户的租户详情
        """
        resp = api_client.get(reverse("person_center.tenant_users.retrieve", kwargs={"id": additional_tenant_user.id}))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_additional_tenant_user_from_additional_natural_user(
        self,
        api_client,
        tenant_users,
        natural_user,
        additional_natural_user,
        additional_tenant_user,
    ):
        """
        绑定自然人情况下，测试和当前用户非同一自然人用户的租户详情
        """

        resp = api_client.get(reverse("person_center.tenant_users.retrieve", kwargs={"id": additional_tenant_user.id}))
        assert resp.status_code == status.HTTP_403_FORBIDDEN


class TestTenantUserChangeEmail:
    def _call_update_email_api(self, api_client: APIClient, tenant_user_id: str, email_data: Dict):
        return api_client.patch(
            reverse("person_center.tenant_users.email.patch", kwargs={"id": tenant_user_id}),
            data=email_data,
        )

    def _check_email_data(self, tenant_user_id: str, email_data: Dict):
        tenant_user = TenantUser.objects.get(id=tenant_user_id)
        assert tenant_user.is_inherited_email == email_data["is_inherited_email"]
        if not email_data["is_inherited_email"]:
            assert tenant_user.custom_email == email_data["custom_email"]

    @pytest.mark.parametrize(
        "invalidated_update_email_data",
        [
            {},
            {"is_inherited_email": False},
            {"is_inherited_email": False, "custom_email": "test"},
            {"is_inherited_email": False, "custom_email": "test@q"},
            {"is_inherited_email": False, "custom_email": "test@q@q.com"},
            {"is_inherited_email": False, "custom_email": "test.com"},
            {"is_inherited_email": ""},
            {"is_inherited_email": "test"},
        ],
    )
    def test_tenant_user_change_email_with_invalidated_email_data(
        self, api_client, bk_user, invalidated_update_email_data
    ):
        current_tenant_user_id = bk_user.get_property("bk_username")
        resp = self._call_update_email_api(api_client, current_tenant_user_id, invalidated_update_email_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        "update_email_data",
        [
            {"is_inherited_email": False, "custom_email": "test@qq.com"},
            {"is_inherited_email": True},
        ],
    )
    def test_tenant_user_change_email_with_no_bound_natural_user(
        self,
        api_client,
        bk_user,
        tenant_users,
        default_tenant,
        random_tenant_users,
        random_tenant,
        additional_tenant_user,
        default_data_source,
        update_email_data,
    ):
        current_tenant_user_id = bk_user.get_property("bk_username")
        # 当前租户用户修改
        resp = self._call_update_email_api(api_client, current_tenant_user_id, update_email_data)
        assert resp.status_code == status.HTTP_200_OK
        self._check_email_data(current_tenant_user_id, update_email_data)

        # 同一数据源用户下的其他租户用户
        random_tenant_user = TenantUser.objects.get(
            data_source=default_data_source, data_source_user__username=bk_user.username, tenant_id=random_tenant
        )
        resp = self._call_update_email_api(api_client, random_tenant_user.id, update_email_data)
        assert resp.status_code == status.HTTP_200_OK
        self._check_email_data(random_tenant_user.id, update_email_data)

        # 同一数据源下其他数据源用户的租户用户
        resp = self._call_update_email_api(api_client, additional_tenant_user.id, update_email_data)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        "update_email_data",
        [
            {"is_inherited_email": False, "custom_email": "test@qq.com"},
            {"is_inherited_email": True},
        ],
    )
    def test_tenant_user_change_email_with_natural_user(
        self, api_client, natural_user, tenant_users, random_tenant_users, random_tenant, update_email_data
    ):
        """
        绑定自然人的情况下，可修改当前自然人任一租户用户，
        """
        for user in [*tenant_users, *random_tenant_users]:
            resp = self._call_update_email_api(api_client, user.id, update_email_data)
            assert resp.status_code == status.HTTP_200_OK
            self._check_email_data(user.id, update_email_data)

    @pytest.mark.parametrize(
        "update_email_data",
        [
            {"is_inherited_email": False, "custom_email": "test@qq.com"},
            {"is_inherited_email": True},
        ],
    )
    def test_tenant_user_change_email_without_natural_user(
        self, api_client, bk_user, default_data_source, tenant_users, random_tenant_users, update_email_data
    ):
        tenant_users = TenantUser.objects.exclude(
            data_source_user__username=bk_user.username,
            data_source=default_data_source,
        )
        for user in tenant_users:
            resp = self._call_update_email_api(api_client, user.id, update_email_data)
            assert resp.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        "update_email_data",
        [
            {"is_inherited_email": False, "custom_email": "test@qq.com"},
            {"is_inherited_email": True},
        ],
    )
    def test_additional_tenant_user_from_additional_natural_user_change_email(
        self, api_client, additional_tenant_user, additional_natural_user, update_email_data
    ):
        resp = self._call_update_email_api(api_client, additional_tenant_user.id, update_email_data)
        assert resp.status_code == status.HTTP_403_FORBIDDEN


class TestTenantUserChangePhone:
    def _call_update_tenant_user_phone_api(self, api_client: APIClient, tenant_user_id: str, phone_data: Dict):
        return api_client.patch(
            reverse("person_center.tenant_users.phone.patch", kwargs={"id": tenant_user_id}),
            data=phone_data,
        )

    def _check_tenant_user_phone_data(self, tenant_user_id: str, phone_data: Dict):
        tenant_user = TenantUser.objects.get(id=tenant_user_id)
        assert tenant_user.is_inherited_phone == phone_data["is_inherited_phone"]
        if not phone_data["is_inherited_phone"]:
            assert tenant_user.custom_phone == phone_data["custom_phone"]
            if custom_phone_country_code := phone_data.get("custom_phone_country_code"):
                assert tenant_user.custom_phone_country_code == custom_phone_country_code

    @pytest.mark.parametrize(
        "invalidated_update_phone_data",
        [
            {},
            {"is_inherited_phone": False},
            {"is_inherited_phone": False, "custom_phone": "test@qq.com"},
            {"is_inherited_phone": False, "custom_phone": ""},
            {"is_inherited_phone": False, "custom_phone": 123},
            {"is_inherited_phone": False, "custom_phone": 131234567891},
            {"is_inherited_email": ""},
            {"is_inherited_email": "test"},
        ],
    )
    def test_tenant_user_change_phone_with_invalidated_email_data(
        self, api_client, bk_user, invalidated_update_phone_data
    ):
        current_tenant_user_id = bk_user.get_property("bk_username")
        resp = self._call_update_tenant_user_phone_api(
            api_client, current_tenant_user_id, invalidated_update_phone_data
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        "update_phone_data",
        [
            {"is_inherited_phone": False, "custom_phone": "13123456789"},
            {"is_inherited_phone": True},
        ],
    )
    def test_tenant_user_change_phone_with_no_bound_natural_user(
        self,
        api_client,
        bk_user,
        tenant_users,
        default_tenant,
        random_tenant_users,
        random_tenant,
        additional_tenant_user,
        default_data_source,
        update_phone_data,
    ):
        current_tenant_user_id = bk_user.get_property("bk_username")
        # 当前租户用户修改
        resp = self._call_update_tenant_user_phone_api(api_client, current_tenant_user_id, update_phone_data)
        assert resp.status_code == status.HTTP_200_OK
        self._check_tenant_user_phone_data(current_tenant_user_id, update_phone_data)

        # 同一数据源用户下的其他租户用户
        random_tenant_user = TenantUser.objects.get(
            data_source=default_data_source, data_source_user__username=bk_user.username, tenant_id=random_tenant
        )
        resp = self._call_update_tenant_user_phone_api(api_client, random_tenant_user.id, update_phone_data)
        assert resp.status_code == status.HTTP_200_OK
        self._check_tenant_user_phone_data(random_tenant_user.id, update_phone_data)

        # 同一数据源下的其他租户用户
        resp = self._call_update_tenant_user_phone_api(api_client, additional_tenant_user.id, update_phone_data)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        "update_phone_data",
        [
            {"is_inherited_phone": False, "custom_phone": "13123456789"},
            {"is_inherited_phone": True},
        ],
    )
    def test_tenant_user_change_phone_with_natural_user(
        self, api_client, natural_user, tenant_users, random_tenant_users, random_tenant, update_phone_data
    ):
        """
        绑定自然人的情况下，可修改当前自然人任一租户用户，
        """
        for user in [*tenant_users, *random_tenant_users]:
            resp = self._call_update_tenant_user_phone_api(api_client, user.id, update_phone_data)
            assert resp.status_code == status.HTTP_200_OK
            self._check_tenant_user_phone_data(user.id, update_phone_data)

    @pytest.mark.parametrize(
        "update_phone_data",
        [
            {"is_inherited_phone": False, "custom_phone": 13123456789},
            {"is_inherited_email": True},
        ],
    )
    def test_tenant_user_change_phone_without_natural_user(
        self, api_client, bk_user, default_data_source, tenant_users, random_tenant_users, update_phone_data
    ):
        tenant_users = TenantUser.objects.exclude(
            data_source_user__username=bk_user.username,
            data_source=default_data_source,
        )
        for user in tenant_users:
            resp = self._call_update_tenant_user_phone_api(api_client, user.id, update_phone_data)
            assert resp.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        "update_phone_data",
        [
            {"is_inherited_phone": False, "custom_phone": 13123456789},
            {"is_inherited_email": True},
        ],
    )
    def test_additional_tenant_user_from_additional_natural_user_change_phone(
        self, api_client, additional_tenant_user, additional_natural_user, update_phone_data
    ):
        resp = self._call_update_tenant_user_phone_api(api_client, additional_tenant_user.id, update_phone_data)
        assert resp.status_code == status.HTTP_403_FORBIDDEN