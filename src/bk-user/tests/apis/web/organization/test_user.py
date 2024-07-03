# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from typing import Any, Dict, List

import pytest
from bkuser.apps.data_source.models import (
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.tenant.models import TenantDepartment, TenantUser, TenantUserCustomField
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from tests.test_utils.helpers import generate_random_string

pytestmark = pytest.mark.django_db


class TestTenantUserSearchApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_single_tenant(self, api_client, random_tenant):
        resp = api_client.get(reverse("organization.tenant_user.search"), data={"keyword": "iu"})

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 3  # noqa: PLR2004  magic number here is ok

        assert {u["username"] for u in resp.data} == {"zhaoliu", "liuqi", "yangjiu"}
        assert {u["full_name"] for u in resp.data} == {"赵六", "柳七", "杨九"}
        assert all(u["tenant_id"] == random_tenant.id for u in resp.data)
        assert all(u["status"] == "enabled" for u in resp.data)
        assert {p for u in resp.data for p in u["organization_paths"]} == {
            "公司/部门A/中心AA",
            "公司/部门A/中心AA/小组AAA",
            "公司/部门A/中心AB",
        }

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    @pytest.mark.usefixtures("_init_collaboration_users_depts")
    def test_multi_tenant(self, api_client, random_tenant, collaboration_tenant):
        resp = api_client.get(reverse("organization.tenant_user.search"), data={"keyword": "hi"})

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 6  # noqa: PLR2004  magic number here is ok

        assert {u["username"] for u in resp.data} == {"lushi", "linshiyi", "baishier"}
        assert {u["tenant_id"] for u in resp.data} == {random_tenant.id, collaboration_tenant.id}
        assert {p for u in resp.data for p in u["organization_paths"]} == {
            "公司/部门A/中心AB/小组ABA",
            "公司/部门B/中心BA",
            "公司/部门B/中心BA/小组BAA",
        }

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_search_full_name(self, api_client, random_tenant):
        resp = api_client.get(reverse("organization.tenant_user.search"), data={"keyword": "十一"})

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1  # noqa: PLR2004  magic number here is ok

        assert resp.data[0]["username"] == "linshiyi"
        assert resp.data[0]["full_name"] == "林十一"

    def test_match_nothing(self, api_client):
        resp = api_client.get(reverse("organization.tenant_department.search"), data={"keyword": "2887"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0


class TestOptionalTenantUserListApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_search_username(self, api_client, random_tenant):
        resp = api_client.get(reverse("organization.optional_leader.list"), data={"keyword": "shi"})

        assert resp.status_code == status.HTTP_200_OK
        assert {user["username"] for user in resp.data} == {"lushi", "linshiyi", "baishier"}
        assert {user["full_name"] for user in resp.data} == {"鲁十", "林十一", "白十二"}

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_search_full_name(self, api_client, random_tenant):
        resp = api_client.get(reverse("organization.optional_leader.list"), data={"keyword": "十二"})

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1  # noqa: PLR2004  magic number here is ok
        assert resp.data[0]["username"] == "baishier"

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_search_with_excluded_user(self, api_client, random_tenant):
        baishier = TenantUser.objects.get(data_source_user__username="baishier", tenant=random_tenant)
        resp = api_client.get(
            reverse("organization.optional_leader.list"),
            data={"keyword": "shi", "excluded_user_id": baishier.id},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert {user["username"] for user in resp.data} == {"lushi", "linshiyi"}


class TestTenantUserListApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_current_tenant_root_dept(self, api_client, random_tenant):
        """测试获取本租户的用户（从根部门起）"""
        url = reverse("organization.tenant_user.list_create", kwargs={"id": random_tenant.id})

        # 根部门层级的用户
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1  # noqa: PLR2004  magic number here is ok
        assert resp.data["results"][0]["username"] == "freedom"

        # 所有层级的用户（根部门递归）
        resp = api_client.get(url, data={"recursive": True, "department_id": 0})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 11  # noqa: PLR2004
        assert len(resp.data["results"]) == 10  # noqa: PLR2004

        # 所有层级的用户（根部门递归）+ 关键字搜索
        resp = api_client.get(url, data={"recursive": True, "department_id": 0, "keyword": "shi"})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 3  # noqa: PLR2004
        assert {user["username"] for user in resp.data["results"]} == {"lushi", "linshiyi", "baishier"}

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_current_tenant_sub_dept(self, api_client, random_tenant):
        """测试获取本租户的用户（从子部门起）"""
        dept_b = TenantDepartment.objects.get(data_source_department__name="部门B", tenant=random_tenant)
        url = reverse("organization.tenant_user.list_create", kwargs={"id": random_tenant.id})

        # 部门 B 层级的用户
        resp = api_client.get(url, data={"recursive": False, "department_id": dept_b.id})
        assert resp.status_code == status.HTTP_200_OK
        assert {user["username"] for user in resp.data["results"]} == {"wangwu"}

        # 部门 B 及其子部门的用户
        resp = api_client.get(url, data={"recursive": True, "department_id": dept_b.id})
        assert resp.status_code == status.HTTP_200_OK
        assert {user["username"] for user in resp.data["results"]} == {"wangwu", "lushi", "baishier"}

        # 部门 B 及其子部门的用户 + 关键字搜索
        resp = api_client.get(url, data={"recursive": True, "department_id": dept_b.id, "keyword": "王五"})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1  # noqa: PLR2004

        wangwu = resp.data["results"][0]
        assert wangwu["username"] == "wangwu"
        assert wangwu["departments"] == ["部门A", "部门B"]

    @pytest.mark.usefixtures("_init_collaboration_users_depts")
    def test_collaboration_tenant(self, api_client, random_tenant, collaboration_tenant):
        """测试获取协同租户的用户"""
        url = reverse("organization.tenant_user.list_create", kwargs={"id": collaboration_tenant.id})
        # 根部门，不递归
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1  # noqa: PLR2004  magic number here is ok

        dept_a = TenantDepartment.objects.get(data_source_department__name="部门A", tenant=random_tenant)
        # 子部门，递归
        resp = api_client.get(url, data={"recursive": True, "department_id": dept_a.id})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 8  # noqa: PLR2004

        # 子部门，递归 + 关键字搜索，虽然李四在部门 A & 中心 AA 中，但是同一个人，只有一条记录
        resp = api_client.get(url, data={"recursive": True, "department_id": dept_a.id, "keyword": "李四"})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1  # noqa: PLR2004
        assert resp.data["results"][0]["username"] == "lisi"


class TestTenantUserCreateApi:
    @pytest.fixture()
    def tenant_user_data(self, random_tenant) -> Dict[str, Any]:
        username = generate_random_string()
        return {
            "username": username,
            "full_name": "这里放一个姓名",
            "email": f"{username}@example.com",
            "phone": "12345678901",
            "phone_country_code": "86",
            "extras": {
                f"{random_tenant.id}_age": 18,
                f"{random_tenant.id}_gender": "male",
                f"{random_tenant.id}_region": "shenzhen",
                f"{random_tenant.id}_hobbies": ["shopping", "reading"],
            },
            "department_ids": [],
            "leader_ids": [],
        }

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_standard(self, api_client, random_tenant, tenant_user_data):
        # 在部门 B 下放一个新用户，设置其 leader 为 wangwu
        dept_b = TenantDepartment.objects.get(data_source_department__name="部门B", tenant=random_tenant)
        wangwu = TenantUser.objects.get(data_source_user__username="wangwu", tenant=random_tenant)
        tenant_user_data.update({"department_ids": [dept_b.id], "leader_ids": [wangwu.id]})

        resp = api_client.post(
            reverse("organization.tenant_user.list_create", kwargs={"id": random_tenant.id}), data=tenant_user_data
        )

        assert resp.status_code == status.HTTP_201_CREATED

        username = tenant_user_data["username"]
        tenant_user = TenantUser.objects.get(id=resp.data["id"])
        assert tenant_user.data_source_user.username == username

        # 检查存在 部门 B -> 新用户的关联边
        assert DataSourceDepartmentUserRelation.objects.filter(
            user_id=tenant_user.data_source_user_id, department_id=dept_b.data_source_department_id
        ).exists()
        # 检查存在 wangwu -> 新用户的关联边
        assert DataSourceUserLeaderRelation.objects.filter(
            user_id=tenant_user.data_source_user_id, leader_id=wangwu.data_source_user_id
        ).exists()

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_invalid_username(self, api_client, random_tenant, tenant_user_data):
        url = reverse("organization.tenant_user.list_create", kwargs={"id": random_tenant.id})

        tenant_user_data["username"] = "%%%"
        resp = api_client.post(url, data=tenant_user_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "不符合 用户名 的命名规范" in resp.data["message"]

        tenant_user_data["username"] = "wangwu"
        resp = api_client.post(url, data=tenant_user_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "用户名 wangwu 已存在" in resp.data["message"]

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_invalid_department_ids(self, api_client, random_tenant, tenant_user_data):
        url = reverse("organization.tenant_user.list_create", kwargs={"id": random_tenant.id})

        tenant_user_data["department_ids"] = [-1]
        resp = api_client.post(url, data=tenant_user_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "指定的部门 {-1} 不存在" in resp.data["message"]

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_invalid_leader_ids(self, api_client, random_tenant, tenant_user_data):
        url = reverse("organization.tenant_user.list_create", kwargs={"id": random_tenant.id})

        tenant_user_data["leader_ids"] = ["not_exists"]
        resp = api_client.post(url, data=tenant_user_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "指定的直属上级 not_exists 不存在" in resp.data["message"]

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_invalid_extras(self, api_client, random_tenant, tenant_user_data):
        url = reverse("organization.tenant_user.list_create", kwargs={"id": random_tenant.id})

        tenant_user_data["extras"] = {"invalid": "invalid"}
        resp = api_client.post(url, data=tenant_user_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "提供的自定义字段数据与租户自定义字段不匹配" in resp.data["message"]

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_valid_logo_png(self, api_client, random_tenant, tenant_user_data):
        url = reverse("organization.tenant_user.list_create", kwargs={"id": random_tenant.id})

        logo_data = "data:image/png;base64,QAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQoMDAsKCwsNDhIQDQ4ERMUFRUVDA8XGBYUGBIU"
        tenant_user_data["logo"] = logo_data
        resp = api_client.post(url, data=tenant_user_data)
        assert resp.status_code == status.HTTP_201_CREATED

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_valid_logo_jpg(self, api_client, random_tenant, tenant_user_data):
        url = reverse("organization.tenant_user.list_create", kwargs={"id": random_tenant.id})

        logo_data = "data:image/jpg;base64,QAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQoMDAsKCwsNDhIQDQ4ERMUFRUVDA8XGBYUGBIU"
        tenant_user_data["logo"] = logo_data
        resp = api_client.post(url, data=tenant_user_data)
        assert resp.status_code == status.HTTP_201_CREATED

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_invalid_logo_format(self, api_client, random_tenant, tenant_user_data):
        url = reverse("organization.tenant_user.list_create", kwargs={"id": random_tenant.id})

        logo_data = "data:application/zip;base64,QAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQoMDAsKCwsNDhIQDQ4ERMUFRUVDA8XGBYUGBIU"
        tenant_user_data["logo"] = logo_data
        resp = api_client.post(url, data=tenant_user_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "Logo 文件只能为 png 或 jpg 格式" in resp.data["message"]


class TestTenantUserUpdateApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_update(self, api_client, random_tenant):
        # 正常的情况
        tenant_user_data: Dict[str, Any] = {
            "username": "wangwu-pro-max",
            "full_name": "这里放一个姓名",
            "email": "wangwu@example.com",
            "phone": "12345678901",
            "phone_country_code": "86",
            "extras": {
                f"{random_tenant.id}_age": 18,
                f"{random_tenant.id}_gender": "male",
                f"{random_tenant.id}_region": "shenzhen",
                f"{random_tenant.id}_hobbies": ["reading", "shopping"],
            },
            "department_ids": [],
            "leader_ids": [],
        }

        wangwu = TenantUser.objects.get(data_source_user__username="wangwu", tenant=random_tenant)
        url = reverse("organization.tenant_user.retrieve_update_destroy", kwargs={"id": wangwu.id})
        resp = api_client.put(url, data=tenant_user_data)
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        # 修改不能编辑的字段
        TenantUserCustomField.objects.filter(
            tenant=random_tenant,
            name=f"{random_tenant.id}_age",
        ).update(manager_editable=False)

        tenant_user_data["extras"].update(
            {
                f"{random_tenant.id}_age": 19,
                f"{random_tenant.id}_region": "beijing",
            }
        )

        resp = api_client.put(url, data=tenant_user_data)
        # 能成功，但是 DB 中的数据不会更新
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        wangwu.refresh_from_db()
        extras = wangwu.data_source_user.extras
        assert extras[f"{random_tenant.id}_age"] == 18  # noqa: PLR2004  magic number here is ok
        assert extras[f"{random_tenant.id}_region"] == "beijing"

        # 把自己设置为自己的 leader
        tenant_user_data["leader_ids"] = [wangwu.id]
        resp = api_client.put(url, data=tenant_user_data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "不能设置自己为自己的直接上级" in resp.data["message"]


class TestTenantUserRetrieveApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_standard(self, api_client, random_tenant):
        # lushi 属于小组 ABA & 中心 BA，有 maiba 和 wangwu 两个 leader
        lushi = TenantUser.objects.get(data_source_user__username="lushi", tenant=random_tenant)
        resp = api_client.get(reverse("organization.tenant_user.retrieve_update_destroy", kwargs={"id": lushi.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["username"] == "lushi"
        assert {dept["name"] for dept in resp.data["departments"]} == {"中心BA", "小组ABA"}
        assert {ld["username"] for ld in resp.data["leaders"]} == {"wangwu", "maiba"}

    @pytest.mark.usefixtures("_init_collaboration_users_depts")
    def test_collaboration_tenant(
        self,
        api_client,
        random_tenant,
        collaboration_tenant,
        random_tenant_custom_fields,
        collaboration_tenant_custom_fields,
    ):
        lushi = TenantUser.objects.get(data_source_user__username="lushi", tenant=random_tenant)
        # 初始化源租户自定义字段信息（使用默认值）
        lushi.data_source_user.extras = {f.name: f.default for f in collaboration_tenant_custom_fields}
        lushi.data_source_user.save()

        resp = api_client.get(reverse("organization.tenant_user.retrieve_update_destroy", kwargs={"id": lushi.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["username"] == "lushi"
        # 字段默认值都是一样的，只是 name 不同，初始化的是包含协同租户 ID 的 name，这里拿到的是
        # 包含当前租户 Id 的 name（需要注意的是，hobbies 字段在协同策略中没配置映射，因此这里不会有）
        assert resp.data["extras"] == {
            f.name: f.default for f in random_tenant_custom_fields if "hobbies" not in f.name
        }


class TestTenantUserDestroyApi:
    @pytest.mark.usefixtures("_init_tenant_users_depts")
    @pytest.mark.usefixtures("_init_collaboration_users_depts")
    def test_standard(self, api_client, random_tenant, collaboration_tenant):
        cur_tenant_wangwu = TenantUser.objects.get(
            data_source_user__username="wangwu",
            data_source__owner_tenant_id=random_tenant.id,
            tenant=random_tenant,
        )

        resp = api_client.delete(
            reverse(
                "organization.tenant_user.retrieve_update_destroy",
                kwargs={"id": cur_tenant_wangwu.id},
            )
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        collaboration_tenant_wangwu = TenantUser.objects.get(
            data_source_user__username="wangwu",
            data_source__owner_tenant_id=collaboration_tenant.id,
            tenant=random_tenant,
        )
        resp = api_client.delete(
            reverse(
                "organization.tenant_user.retrieve_update_destroy",
                kwargs={"id": collaboration_tenant_wangwu.id},
            )
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "仅可删除非协同产生的租户用户" in resp.data["message"]


class TestTenantUserOrganizationPathListApi:
    """测试获取租户的组织架构路径"""

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_standard(self, api_client, random_tenant):
        lushi = TenantUser.objects.get(data_source_user__username="lushi", tenant=random_tenant)
        resp = api_client.get(reverse("organization.tenant_user.organization_path.list", kwargs={"id": lushi.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["organization_paths"] == ["公司/部门A/中心AB/小组ABA", "公司/部门B/中心BA"]


class TestTenantUserStatusUpdateApi:
    """测试切换用户状态"""

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_standard(self, api_client, random_tenant):
        lisi = TenantUser.objects.get(data_source_user__username="lisi", tenant=random_tenant)
        url = reverse("organization.tenant_user.status.update", kwargs={"id": lisi.id})

        # 默认是启用，切换一次变成禁用
        resp = api_client.put(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == "disabled"

        # 切换一次变成启用
        resp = api_client.put(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == "enabled"


class TestTenantUserBatchCreateAndPreviewApi:
    """测试快速录入（批量创建）用户 * 预览 API"""

    @pytest.fixture()
    def raw_user_infos(self) -> List[str]:
        # username full_name email phone age gender region hobbies
        return [
            "star, Star, trailblazer@railway.com, +8613612345671, 1, female, Nameless, dancing/collecting/traveling",
            "kafka, Kafka, kafka@railway.com, +4915123456789, 32, female, StarCoreHunter, shopping/hunting",
            "sam, FireFly, sam@railway.com, +447700123456, 23, female, StarCoreHunter, singing/eating/sleeping",
            "404, SilverWolf, 404@railway.com, +79123456789, 16, female, StarCoreHunter, gaming/hacking",
            "dotKnifeBoy, Blade, blade@railway.com, +8613612345675, 48, male, StarCoreHunter, studying/driving",
        ]

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_preview(self, api_client, random_tenant, random_tenant_custom_fields, raw_user_infos):
        company = TenantDepartment.objects.get(data_source_department__name="公司", tenant=random_tenant)
        age_field, gender_field, region_field, hobbies_field = random_tenant_custom_fields

        resp = api_client.post(
            reverse("organization.tenant_user.batch_create_preview"),
            data={"user_infos": raw_user_infos, "department_id": company.id},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data == [
            {
                "username": "star",
                "full_name": "Star",
                "email": "trailblazer@railway.com",
                "phone": "13612345671",
                "phone_country_code": "86",
                "extras": {
                    age_field.name: 1,
                    gender_field.name: "female",
                    region_field.name: "Nameless",
                    hobbies_field.name: ["dancing", "collecting", "traveling"],
                },
            },
            {
                "username": "kafka",
                "full_name": "Kafka",
                "email": "kafka@railway.com",
                "phone": "15123456789",
                "phone_country_code": "49",
                "extras": {
                    age_field.name: 32,
                    gender_field.name: "female",
                    region_field.name: "StarCoreHunter",
                    hobbies_field.name: ["shopping", "hunting"],
                },
            },
            {
                "username": "sam",
                "full_name": "FireFly",
                "email": "sam@railway.com",
                "phone": "7700123456",
                "phone_country_code": "44",
                "extras": {
                    age_field.name: 23,
                    gender_field.name: "female",
                    region_field.name: "StarCoreHunter",
                    hobbies_field.name: ["singing", "eating", "sleeping"],
                },
            },
            {
                "username": "404",
                "full_name": "SilverWolf",
                "email": "404@railway.com",
                "phone": "9123456789",
                "phone_country_code": "7",
                "extras": {
                    age_field.name: 16,
                    gender_field.name: "female",
                    region_field.name: "StarCoreHunter",
                    hobbies_field.name: ["gaming", "hacking"],
                },
            },
            {
                "username": "dotKnifeBoy",
                "full_name": "Blade",
                "email": "blade@railway.com",
                "phone": "13612345675",
                "phone_country_code": "86",
                "extras": {
                    age_field.name: 48,
                    gender_field.name: "male",
                    region_field.name: "StarCoreHunter",
                    hobbies_field.name: ["studying", "driving"],
                },
            },
        ]

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_create(self, api_client, random_tenant, random_tenant_custom_fields, raw_user_infos):
        company = TenantDepartment.objects.get(data_source_department__name="公司", tenant=random_tenant)
        age_field, gender_field, region_field, hobbies_field = random_tenant_custom_fields

        resp = api_client.post(
            reverse("organization.tenant_user.batch_create"),
            data={"user_infos": raw_user_infos, "department_id": company.id},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        relations = DataSourceDepartmentUserRelation.objects.filter(department_id=company.data_source_department_id)
        assert {r.user.username for r in relations} == {"star", "kafka", "sam", "404", "dotKnifeBoy", "zhangsan"}

        fire_fly = TenantUser.objects.get(data_source_user__username="sam", tenant=random_tenant).data_source_user
        assert fire_fly.full_name == "FireFly"
        assert fire_fly.email == "sam@railway.com"
        assert fire_fly.phone == "7700123456"
        assert fire_fly.phone_country_code == "44"
        assert fire_fly.extras == {
            age_field.name: 23,
            gender_field.name: "female",
            region_field.name: "StarCoreHunter",
            hobbies_field.name: ["singing", "eating", "sleeping"],
        }

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_invalid_case(self, api_client, random_tenant, random_tenant_custom_fields, raw_user_infos):
        url = reverse("organization.tenant_user.batch_create")
        company = TenantDepartment.objects.get(data_source_department__name="公司", tenant=random_tenant)

        raw_user_infos.append(
            "dotKnifeBoy, Blade, blade@railway.com, +8613612345675, 48, male, StarCoreHunter, studying/driving"
        )
        resp = api_client.post(url, data={"user_infos": raw_user_infos, "department_id": company.id})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "用户名 dotknifeboy 重复" in resp.data["message"]

        raw_user_infos[-1] = "lisi, 李四, lisi@m.com, +8613612345678, 55, male, shenzhen, reading/driving"
        resp = api_client.post(url, data={"user_infos": raw_user_infos, "department_id": company.id})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "用户名 lisi 已存在" in resp.data["message"]

        raw_user_infos[-1] = "meishisan, 梅十三, meishisan@m.com, +8613612345678, 55, male, shenzhen"
        resp = api_client.post(url, data={"user_infos": raw_user_infos, "department_id": company.id})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "第 6 行，用户信息格式不正确，预期 8 个字段，实际 7 个字段" in resp.data["message"]

        raw_user_infos[-1] = "meishisan, 梅十三, meishisan@m.com, +x-xxxx, 55, male, shenzhen, reading/driving"
        resp = api_client.post(url, data={"user_infos": raw_user_infos, "department_id": company.id})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "第 6 行，手机号 +x-xxxx 格式不正确" in resp.data["message"]

        raw_user_infos[-1] = "aiwu, 艾五, aiwu@m.com, +8613612345678, 55, helicopter, shenzhen, reading/driving"
        resp = api_client.post(url, data={"user_infos": raw_user_infos, "department_id": company.id})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "helicopter 不在可选项" in resp.data["message"]

        raw_user_infos[-1] = "aiwu, 艾五, aiwu@m.com, +8613612345678, 55, male, shenzhen, jumping/driving"
        resp = api_client.post(url, data={"user_infos": raw_user_infos, "department_id": company.id})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "不在可选项" in resp.data["message"]

        raw_user_infos[-1] = "aiwu, 艾五, aiwu@m.com, +8613612345678, 1k, male, shenzhen, reading/driving"
        resp = api_client.post(url, data={"user_infos": raw_user_infos, "department_id": company.id})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "值 1k 不能转换为数字" in resp.data["message"]


class TestTenantUserBatchDeleteApi:
    """测试批量删除租户用户"""

    @pytest.mark.usefixtures("_init_tenant_users_depts")
    def test_layoffs(self, api_client, random_tenant):
        user_codes = ["zhangsan", "lisi", "wangwu", "liuqi", "lushi", "linshiyi", "baishier"]
        user_ids = TenantUser.objects.filter(
            tenant=random_tenant,
            data_source_user__code__in=user_codes,
        ).values_list("id", flat=True)

        resp = api_client.delete(
            reverse("organization.tenant_user.batch_delete"),
            QUERY_STRING=urlencode({"user_ids": ",".join(user_ids)}, doseq=True),
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        assert not TenantUser.objects.filter(id__in=user_ids).exists()
        assert not DataSourceUser.objects.filter(code__in=user_codes).exists()
        assert not DataSourceDepartmentUserRelation.objects.filter(user__code__in=user_codes).exists()
        assert not DataSourceDepartmentUserRelation.objects.filter(user__code__in=user_codes).exists()
        assert not DataSourceUserLeaderRelation.objects.filter(user__code__in=user_codes).exists()
        assert not DataSourceUserLeaderRelation.objects.filter(leader__code__in=user_codes).exists()
