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
import string
from unittest import mock
from urllib.parse import parse_qs, urlparse

import pytest
from bkuser.apis.web.password.constants import TokenRelatedObjType
from bkuser.apis.web.password.tokens import UserResetPasswordTokenManager
from bkuser.apps.data_source.models import LocalDataSourceIdentityInfo
from bkuser.apps.tenant.models import TenantUser
from bkuser.common.hashers import check_password
from bkuser.common.verification_code import VerificationCodeManager, VerificationCodeScene
from django.test.utils import override_settings
from django.urls import reverse
from rest_framework import status

from tests.test_utils.data_source import init_local_data_source_identity_infos
from tests.test_utils.helpers import generate_random_string
from tests.test_utils.tenant import sync_users_depts_to_tenant

pytestmark = pytest.mark.django_db


@pytest.fixture()
def tenant_user(random_tenant, full_local_data_source) -> TenantUser:
    init_local_data_source_identity_infos(full_local_data_source)
    sync_users_depts_to_tenant(random_tenant, full_local_data_source)
    return TenantUser.objects.filter(tenant=random_tenant, data_source_id=full_local_data_source.id).first()


class TestResetPasswordByPhoneAfterForget:
    """忘记密码后通过手机找回"""

    @pytest.fixture(autouse=True)
    def _mock_cmsi_component(self):
        with mock.patch(
            "bkuser.component.cmsi.send_mail",
            return_value=None,
        ), mock.patch(
            "bkuser.component.cmsi.send_sms",
            return_value=None,
        ):
            yield

    def test_standard(self, api_client, tenant_user):
        # 1. 模拟发送验证码
        phone, phone_country_code = tenant_user.phone_info
        resp = api_client.post(
            reverse("password.send_verification_code"),
            data={"tenant_id": tenant_user.tenant_id, "phone": phone, "phone_country_code": phone_country_code},
        )

        assert resp.status_code == status.HTTP_204_NO_CONTENT

        # 2. 从缓存中获取验证码用于认证，认证后获取到密码重置链接
        mgr = VerificationCodeManager(phone, phone_country_code, VerificationCodeScene.RESET_PASSWORD)
        code = mgr.cache.get(mgr.code_cache_key)
        resp = api_client.post(
            reverse("password.get_passwd_reset_url_by_verification_code"),
            data={
                "tenant_id": tenant_user.tenant_id,
                "phone": phone,
                "phone_country_code": phone_country_code,
                "verification_code": code,
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        reset_password_url = resp.data["reset_password_url"]
        assert reset_password_url is not None

        # 3. 解析密码重置链接获取 Token
        reset_token = parse_qs(urlparse(reset_password_url).query)["token"][0]

        # 4. 通过 Token 匹配租户用户
        resp = api_client.get(
            reverse("password.list_users_by_reset_passwd_token"),
            data={"token": reset_token},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert tenant_user.id in [user["tenant_user_id"] for user in resp.data]

        # 5. 通过 Token 重置密码，分批次生成再拼接，确保各种字符都有
        new_password = (
            generate_random_string(length=16, chars=string.ascii_letters)
            + generate_random_string(length=8, chars=string.digits)
            + generate_random_string(length=8, chars=string.punctuation)
        )
        resp = api_client.post(
            reverse("password.reset_passwd_by_token"),
            data={
                "tenant_user_id": tenant_user.id,
                "password": new_password,
                "token": reset_token,
            },
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        identity_info = LocalDataSourceIdentityInfo.objects.get(user=tenant_user.data_source_user)
        assert check_password(new_password, identity_info.password)

    def test_send_verification_code_with_invalid_phone(self, api_client, tenant_user):
        phone, phone_country_code = tenant_user.phone_info
        # 修改手机号码导致无效
        phone = phone[:-3] + "555"

        url = reverse("password.send_verification_code")
        data = {"tenant_id": tenant_user.tenant_id, "phone": phone, "phone_country_code": phone_country_code}
        # 安全起见，默认情况下不会有异常
        resp = api_client.post(url, data)
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_send_verification_code_with_invalid_phone_and_raise_exception(self, api_client, tenant_user):
        phone, phone_country_code = tenant_user.phone_info
        # 修改手机号码导致无效
        phone = phone[:-3] + "333"

        url = reverse("password.send_verification_code")
        data = {"tenant_id": tenant_user.tenant_id, "phone": phone, "phone_country_code": phone_country_code}
        with override_settings(ALLOW_RAISE_ERROR_TO_USER_WHEN_RESET_PASSWORD=True):
            resp = api_client.post(url, data)
            assert resp.status_code == status.HTTP_400_BAD_REQUEST
            assert "匹配不到用户" in resp.data["message"]

    def test_get_reset_password_url_with_invalid_phone_or_token(self, api_client, tenant_user):
        # 验证码错误
        url = reverse("password.get_passwd_reset_url_by_verification_code")
        data = {
            "tenant_id": tenant_user.tenant_id,
            "phone": tenant_user.phone_info[0],
            "phone_country_code": tenant_user.phone_info[1],
            "verification_code": "123456",
        }
        resp = api_client.post(url, data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "手机号码或验证码错误" in resp.data["message"]

        # 手机号错误，错误信息应该是一致的
        data["phone"] = data["phone"][:-1] + "5"
        resp = api_client.post(url, data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "手机号码或验证码错误" in resp.data["message"]


class TestResetPasswordByEmailAfterForget:
    """忘记密码后通过邮件找回"""

    @pytest.fixture(autouse=True)
    def _mock_cmsi_component(self):
        with mock.patch(
            "bkuser.component.cmsi.send_mail",
            return_value=None,
        ), mock.patch(
            "bkuser.component.cmsi.send_sms",
            return_value=None,
        ):
            yield

    def test_standard(self, api_client, tenant_user):
        # 1. 发送重置密码链接邮件
        resp = api_client.post(
            reverse("password.send_passwd_reset_email"),
            data={"tenant_id": tenant_user.tenant_id, "email": tenant_user.email},
        )

        assert resp.status_code == status.HTTP_204_NO_CONTENT

        # 2. 搞一个能用的，关联 email 的 token，但是需要先干掉频控锁
        mgr = UserResetPasswordTokenManager()
        lock_key = f"email:{tenant_user.tenant_id}:{tenant_user.email}"
        mgr.cache.delete(lock_key)

        reset_token = mgr.gen_token(tenant_user, TokenRelatedObjType.EMAIL)

        # 3. 通过 Token 匹配租户用户
        resp = api_client.get(
            reverse("password.list_users_by_reset_passwd_token"),
            data={"token": reset_token},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert tenant_user.id in [user["tenant_user_id"] for user in resp.data]

        # 4. 通过 Token 重置密码，分批次生成再拼接，确保各种字符都有
        new_password = (
            generate_random_string(length=16, chars=string.ascii_letters)
            + generate_random_string(length=8, chars=string.digits)
            + generate_random_string(length=8, chars=string.punctuation)
        )
        resp = api_client.post(
            reverse("password.reset_passwd_by_token"),
            data={
                "tenant_user_id": tenant_user.id,
                "password": new_password,
                "token": reset_token,
            },
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        identity_info = LocalDataSourceIdentityInfo.objects.get(user=tenant_user.data_source_user)
        assert check_password(new_password, identity_info.password)

    def test_send_reset_pwd_url_with_invalid_email(self, api_client, tenant_user):
        email = tenant_user.email
        # 修改邮箱导致无效
        email = "xxx" + email

        url = reverse("password.send_passwd_reset_email")
        data = {"tenant_id": tenant_user.tenant_id, "email": email}
        # 安全起见，默认情况下不会有异常
        resp = api_client.post(url, data)
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_send_reset_pwd_url_with_invalid_email_and_raise_exception(self, api_client, tenant_user):
        email = tenant_user.email
        # 修改邮箱导致无效
        email = "yyy" + email

        url = reverse("password.send_passwd_reset_email")
        data = {"tenant_id": tenant_user.tenant_id, "email": email}
        with override_settings(ALLOW_RAISE_ERROR_TO_USER_WHEN_RESET_PASSWORD=True):
            resp = api_client.post(url, data)
            assert resp.status_code == status.HTTP_400_BAD_REQUEST
            assert "匹配不到用户" in resp.data["message"]
