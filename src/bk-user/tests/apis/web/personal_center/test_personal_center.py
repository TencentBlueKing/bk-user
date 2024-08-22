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

import pytest
from bkuser.apis.web.personal_center.constants import PhoneOrEmailUpdateRestrictionEnum
from bkuser.apps.tenant.models import TenantUser
from django.conf import settings
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture()
def tenant_user(bk_user) -> TenantUser:
    return TenantUser.objects.get(tenant_id=bk_user.get_property("tenant_id"), id=bk_user.username)


class TestTenantUserExtrasUpdateApi:
    def test_update(self, api_client, tenant_user, tenant_user_custom_fields):
        resp = api_client.put(
            reverse("personal_center.tenant_users.extras.update", kwargs={"id": tenant_user.id}),
            data={"extras": {"gender": "male", "sport_hobby": ["basketball"]}},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_update_without_all_editable_fields(self, api_client, tenant_user, tenant_user_custom_fields):
        """只指定部分可编辑的字段进行更新是被允许的"""
        resp = api_client.put(
            reverse("personal_center.tenant_users.extras.update", kwargs={"id": tenant_user.id}),
            data={"extras": {"gender": "male"}},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_update_not_editable_field(self, api_client, tenant_user, tenant_user_custom_fields):
        resp = api_client.put(
            reverse("personal_center.tenant_users.extras.update", kwargs={"id": tenant_user.id}),
            data={"extras": {"age": 18}},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "当前用户无可编辑的租户自定义字段" in resp.data["message"]

    def test_update_with_invalid_value_case_1(self, api_client, tenant_user, tenant_user_custom_fields):
        resp = api_client.put(
            reverse("personal_center.tenant_users.extras.update", kwargs={"id": tenant_user.id}),
            data={"extras": {"gender": "make", "sport_hobby": ["basketball"]}},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "字段 性别 的值 make 不是可选项之一" in resp.data["message"]

    def test_update_with_invalid_value_case_2(self, api_client, tenant_user, tenant_user_custom_fields):
        resp = api_client.put(
            reverse("personal_center.tenant_users.extras.update", kwargs={"id": tenant_user.id}),
            data={"extras": {"gender": "female", "sport_hobby": []}},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "多选枚举类型自定义字段值必须是非空列表" in resp.data["message"]

    def test_update_with_invalid_value_case_3(self, api_client, tenant_user, tenant_user_custom_fields):
        resp = api_client.put(
            reverse("personal_center.tenant_users.extras.update", kwargs={"id": tenant_user.id}),
            data={"extras": {"gender": "female", "sport_hobby": ["flying"]}},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "字段 运动爱好 的值 ['flying'] 不是可选项的子集" in resp.data["message"]


class TestTenantUserFieldListApi:
    def test_list(self, api_client, tenant_user, tenant_user_custom_fields):
        resp = api_client.get(reverse("personal_center.tenant_users.fields.list", kwargs={"id": tenant_user.id}))

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["builtin_fields"]) == 5  # noqa: PLR2004
        assert [f["name"] for f in resp.data["custom_fields"]] == ["age", "gender", "sport_hobby"]
        assert [f["name"] for f in resp.data["custom_fields"] if f["editable"]] == ["gender", "sport_hobby"]


class TestTenantUserFeatureFlagListApi:
    def test_list(self, api_client, tenant_user):
        resp = api_client.get(reverse("personal_center.tenant_users.feature_flag.list", kwargs={"id": tenant_user.id}))
        settings.TENANT_PHONE_UPDATE_RESTRICTIONS = {"default": PhoneOrEmailUpdateRestrictionEnum.EDITABLE_DIRECTLY}
        settings.TENANT_EMAIL_UPDATE_RESTRICTIONS = {"default": PhoneOrEmailUpdateRestrictionEnum.NEED_VERIFY}
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["can_change_password"] is False
        assert resp.data["phone_update_restriction"] == "need_verify"
        assert resp.data["email_update_restriction"] == "need_verify"


class TestTenantUserLanguageUpdateApi:
    @pytest.mark.parametrize(
        ("language"),
        [("zh-cn"), ("en")],
    )
    def test_update_legal_language(self, api_client, tenant_user, language):
        resp = api_client.put(
            reverse("personal_center.tenant_users.language.update", kwargs={"id": tenant_user.id}),
            data={"language": language},
        )

        assert resp.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.parametrize(
        ("language"),
        [("zh-US"), ("en-CN"), ""],
    )
    def test_update_illegal_lanague(self, api_client, tenant_user, language):
        resp = api_client.put(
            reverse("personal_center.tenant_users.language.update", kwargs={"id": tenant_user.id}),
            data={"language": language},
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "不是合法选项" in resp.data["message"]


class TestTenantUserTimeZoneUpdateApi:
    @pytest.mark.parametrize(("time_zone"), [("Asia/Shanghai"), ("UTC")])
    def test_update_legal_timezone(self, api_client, tenant_user, time_zone):
        resp = api_client.put(
            reverse("personal_center.tenant_users.time_zone.update", kwargs={"id": tenant_user.id}),
            data={"time_zone": time_zone},
        )

        assert resp.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.parametrize(("time_zone"), [("Asia/Shenzhen"), ("ESC"), ("")])
    def test_update_illegal_timezone(self, api_client, tenant_user, time_zone):
        resp = api_client.put(
            reverse("personal_center.tenant_users.time_zone.update", kwargs={"id": tenant_user.id}),
            data={"time_zone": time_zone},
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "不是合法选项" in resp.data["message"]


class TestTenantUserLogoUpdateApi:
    @pytest.mark.parametrize(
        ("logo_data"),
        [
            ("data:image/jpeg;base64,QAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQoMDAsKCwsNDhIQDQ4ERMUFRUVDA8XGBYUGBIU"),
            ("data:image/png;base64,QAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQoMDAsKCwsNDhIQDQ4ERMUFRUVDA8XGBYUGBIU"),
        ],
    )
    def test_update_legal_logo(self, api_client, tenant_user, logo_data):
        resp = api_client.put(
            reverse("personal_center.tenant_users.logo.update", kwargs={"id": tenant_user.id}),
            data={"logo": logo_data},
        )

        assert resp.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.parametrize(
        ("logo_data"),
        [
            ("data:image/gif;base64,QAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQoMDAsKCwsNDhIQDQ4ERMUFRUVDA8XGBYUGBIU"),
            ("data:application/zip;base64,QAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQoMDAsKCwsNDhIQDQ4ERMUFRUVDA8XGBYUGBIU"),
        ],
    )
    def test_update_illegal_logo(self, api_client, tenant_user, logo_data):
        resp = api_client.put(
            reverse("personal_center.tenant_users.logo.update", kwargs={"id": tenant_user.id}),
            data={"logo": logo_data},
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "Logo 文件只能为 png 或 jpg 格式" in resp.data["message"]


class TestTenantUserPhoneUpdateApi:
    def test_update_phone_success(self, api_client, tenant_user):
        data = {
            "is_inherited_phone": "False",
            "custom_phone": "12345678901",
            "custom_phone_country_code": "86",
        }
        settings.TENANT_PHONE_UPDATE_RESTRICTIONS = {"default": PhoneOrEmailUpdateRestrictionEnum.EDITABLE_DIRECTLY}
        resp = api_client.put(
            reverse("personal_center.tenant_users.phone.update", kwargs={"id": tenant_user.id}), data=data
        )

        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert TenantUser.objects.get(id=tenant_user.id).custom_phone == "12345678901"
        assert TenantUser.objects.get(id=tenant_user.id).custom_phone_country_code == "86"
        assert not TenantUser.objects.get(id=tenant_user.id).is_inherited_phone

    def test_update_phone_not_editable(self, api_client, tenant_user):
        data = {
            "is_inherited_phone": "False",
            "custom_phone": "12345678901",
            "custom_phone_country_code": "86",
        }
        settings.TENANT_PHONE_UPDATE_RESTRICTIONS = {"default": PhoneOrEmailUpdateRestrictionEnum.NOT_EDITABLE}
        resp = api_client.put(
            reverse("personal_center.tenant_users.phone.update", kwargs={"id": tenant_user.id}), data=data
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert TenantUser.objects.get(id=tenant_user.id).custom_phone == tenant_user.custom_phone
        assert (
            TenantUser.objects.get(id=tenant_user.id).custom_phone_country_code
            == tenant_user.custom_phone_country_code
        )
        assert TenantUser.objects.get(id=tenant_user.id).is_inherited_phone == tenant_user.is_inherited_phone


class TestTenantUserEmailUpdateApi:
    def test_update_email_success(self, api_client, tenant_user):
        data = {
            "is_inherited_email": "False",
            "custom_email": "123456@qq.com",
        }

        settings.TENANT_EMAIL_UPDATE_RESTRICTIONS = {"default": PhoneOrEmailUpdateRestrictionEnum.EDITABLE_DIRECTLY}

        resp = api_client.put(
            reverse("personal_center.tenant_users.email.update", kwargs={"id": tenant_user.id}), data=data
        )

        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert TenantUser.objects.get(id=tenant_user.id).custom_email == "123456@qq.com"
        assert not TenantUser.objects.get(id=tenant_user.id).is_inherited_email

    def test_update_email_not_editable(self, api_client, tenant_user):
        data = {
            "is_inherited_email": "False",
            "custom_email": "123456@qq.com",
        }

        settings.TENANT_EMAIL_UPDATE_RESTRICTIONS = {"default": PhoneOrEmailUpdateRestrictionEnum.NOT_EDITABLE}

        resp = api_client.put(
            reverse("personal_center.tenant_users.email.update", kwargs={"id": tenant_user.id}), data=data
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert TenantUser.objects.get(id=tenant_user.id).custom_email == tenant_user.custom_email
        assert TenantUser.objects.get(id=tenant_user.id).is_inherited_email == tenant_user.is_inherited_email
