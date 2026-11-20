# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

from unittest import mock
from urllib.parse import parse_qs, urlparse

import pytest
from bkuser.apis.web.password.constants import TokenRelatedObjType
from bkuser.apis.web.password.tokens import UserResetPasswordTokenManager
from bkuser.apps.data_source.models import DataSource, LocalDataSourceIdentityInfo
from bkuser.apps.idp.constants import IdpStatus
from bkuser.apps.idp.data_models import gen_data_source_match_rule_of_local
from bkuser.apps.idp.models import Idp, IdpDataSourceRelation
from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.idp_data_source import IdpDataSourceRelationHandler
from bkuser.common.hashers import check_password
from bkuser.common.verification_code import PhoneVerificationCodeManager, VerificationCodeScene
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.idp_plugins.local.plugin import LocalIdpPluginConfig
from django.test.utils import override_settings
from django.urls import reverse
from rest_framework import status

from tests.test_utils.data_source import (
    init_data_source_users_depts_and_relations,
    init_local_data_source_identity_infos,
)
from tests.test_utils.tenant import sync_users_depts_to_tenant

pytestmark = pytest.mark.django_db

NEW_PASSWORD = "uric8822IOw039x^#ke&239="


@pytest.fixture
def local_idp(random_tenant, full_local_data_source) -> Idp:
    """生效范围仅包含 full_local_data_source 的本地账密认证源"""
    idp = Idp.objects.create(
        name="local",
        owner_tenant_id=random_tenant.id,
        plugin_id=BuiltinIdpPluginEnum.LOCAL,
        plugin_config=LocalIdpPluginConfig(data_source_ids=[full_local_data_source.id]),
    )
    IdpDataSourceRelationHandler.set_real_relations_from_match_rules(
        idp, [gen_data_source_match_rule_of_local(full_local_data_source.id)]
    )
    return idp


@pytest.fixture
def tenant_user(random_tenant, full_local_data_source, local_idp) -> TenantUser:
    init_local_data_source_identity_infos(full_local_data_source)
    sync_users_depts_to_tenant(random_tenant, full_local_data_source)
    return TenantUser.objects.filter(tenant=random_tenant, data_source_id=full_local_data_source.id).first()


def gen_email_reset_token(tenant_user: TenantUser) -> str:
    mgr = UserResetPasswordTokenManager()
    # 测试中可能多次签发，需要先清理频控锁
    mgr.cache.delete(f"email:{tenant_user.tenant_id}:{tenant_user.email}")
    return mgr.gen_token(tenant_user, TokenRelatedObjType.EMAIL)


class TestResetPasswordByPhoneAfterForget:
    """忘记密码后通过手机找回"""

    @pytest.fixture(autouse=True)
    def _mock_cmsi_component(self):
        with (
            mock.patch(
                "bkuser.component.cmsi.BkEsbCmsiClient.send_mail",
                return_value=None,
            ),
            mock.patch(
                "bkuser.component.cmsi.BkEsbCmsiClient.send_sms",
                return_value=None,
            ),
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
        mgr = PhoneVerificationCodeManager(phone, phone_country_code, VerificationCodeScene.RESET_PASSWORD)
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

        # 5. 通过 Token 重置密码，使用固定密码避免随机生成的密码不符合密码规则
        new_password = "uric8822IOw039x^#ke&239="
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
        with (
            mock.patch(
                "bkuser.component.cmsi.BkEsbCmsiClient.send_mail",
                return_value=None,
            ),
            mock.patch(
                "bkuser.component.cmsi.BkEsbCmsiClient.send_sms",
                return_value=None,
            ),
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

        # 4. 通过 Token 重置密码，使用固定密码避免随机生成的密码不符合密码规则
        new_password = "uric8822IOw039x^#ke&239="
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


class TestResetPasswordRequiresPasswordLogin:
    """只有能使用账密登录的用户才能通过忘记密码重置密码"""

    @pytest.fixture(autouse=True)
    def _mock_cmsi_component(self):
        with (
            mock.patch("bkuser.component.cmsi.BkEsbCmsiClient.send_mail", return_value=None),
            mock.patch("bkuser.component.cmsi.BkEsbCmsiClient.send_sms", return_value=None),
        ):
            yield

    def test_send_reset_pwd_email_when_local_idp_disabled(self, api_client, tenant_user, local_idp):
        Idp.objects.filter(id=local_idp.id).update(status=IdpStatus.DISABLED)

        with override_settings(ALLOW_RAISE_ERROR_TO_USER_WHEN_RESET_PASSWORD=True):
            resp = api_client.post(
                reverse("password.send_passwd_reset_email"),
                data={"tenant_id": tenant_user.tenant_id, "email": tenant_user.email},
            )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "匹配不到用户" in resp.data["message"]

    def test_get_reset_password_url_when_local_idp_disabled(self, api_client, tenant_user, local_idp):
        phone, phone_country_code = tenant_user.phone_info
        mgr = PhoneVerificationCodeManager(phone, phone_country_code, VerificationCodeScene.RESET_PASSWORD)
        # 其他用例可能已为同一手机号生成过验证码，需要先清理频控锁
        mgr.cache.delete(mgr.lock_cache_key)
        code = mgr.gen_code()

        Idp.objects.filter(id=local_idp.id).update(status=IdpStatus.DISABLED)

        resp = api_client.post(
            reverse("password.get_passwd_reset_url_by_verification_code"),
            data={
                "tenant_id": tenant_user.tenant_id,
                "phone": phone,
                "phone_country_code": phone_country_code,
                "verification_code": code,
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "手机号码或验证码错误" in resp.data["message"]

    def test_reset_password_when_local_idp_disabled_after_token_issued(self, api_client, tenant_user, local_idp):
        reset_token = gen_email_reset_token(tenant_user)
        Idp.objects.filter(id=local_idp.id).update(status=IdpStatus.DISABLED)

        resp = api_client.get(reverse("password.list_users_by_reset_passwd_token"), data={"token": reset_token})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data == []

        resp = api_client.post(
            reverse("password.reset_passwd_by_token"),
            data={"tenant_user_id": tenant_user.id, "password": NEW_PASSWORD, "token": reset_token},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "租户用户不存在" in resp.data["message"]

    def test_reset_password_when_out_of_local_idp_scope(self, api_client, tenant_user):
        reset_token = gen_email_reset_token(tenant_user)
        IdpDataSourceRelation.objects.filter(data_source_id=tenant_user.data_source_id).delete()

        resp = api_client.post(
            reverse("password.reset_passwd_by_token"),
            data={"tenant_user_id": tenant_user.id, "password": NEW_PASSWORD, "token": reset_token},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "租户用户不存在" in resp.data["message"]

    def test_reset_password_when_password_disabled(self, api_client, tenant_user):
        reset_token = gen_email_reset_token(tenant_user)
        data_source = DataSource.objects.get(id=tenant_user.data_source_id)
        data_source.plugin_config["enable_password"] = False
        data_source.save(update_fields=["plugin_config", "updated_at"])

        resp = api_client.post(
            reverse("password.reset_passwd_by_token"),
            data={"tenant_user_id": tenant_user.id, "password": NEW_PASSWORD, "token": reset_token},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "租户用户不存在" in resp.data["message"]

    def test_list_users_only_in_local_idp_scope(
        self, api_client, random_tenant, tenant_user, bare_local_data_source_b
    ):
        """同一邮箱在生效范围内外的数据源各有一个账号时，只列出生效范围内的账号"""
        init_data_source_users_depts_and_relations(bare_local_data_source_b)
        init_local_data_source_identity_infos(bare_local_data_source_b)
        sync_users_depts_to_tenant(random_tenant, bare_local_data_source_b)
        out_of_scope_user_ids = set(
            TenantUser.objects.filter_by_email(random_tenant.id, tenant_user.email)
            .filter(data_source_id=bare_local_data_source_b.id)
            .values_list("id", flat=True)
        )
        assert out_of_scope_user_ids

        reset_token = gen_email_reset_token(tenant_user)
        resp = api_client.get(reverse("password.list_users_by_reset_passwd_token"), data={"token": reset_token})

        assert resp.status_code == status.HTTP_200_OK
        listed_user_ids = {user["tenant_user_id"] for user in resp.data}
        assert tenant_user.id in listed_user_ids
        assert not listed_user_ids & out_of_scope_user_ids
