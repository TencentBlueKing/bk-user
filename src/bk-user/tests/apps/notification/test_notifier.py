# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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

import pytest
from bkuser.apps.notification.constants import NotificationMethod, NotificationScene
from bkuser.apps.notification.notifier import ContactNotifier, TenantUserNotifier, UserTmplContextGenerator
from bkuser.apps.tenant.models import TenantUser
from django.conf import settings
from django.test import override_settings

from tests.test_utils.tenant import sync_users_depts_to_tenant

pytestmark = pytest.mark.django_db


class TestTenantUserNotifier:
    """测试租户用户通知功能"""

    @pytest.fixture
    def data_source(self, random_tenant, full_local_data_source):
        sync_users_depts_to_tenant(random_tenant, full_local_data_source)
        return full_local_data_source

    def test_render_tmpl_user_initialize(self, data_source):
        notifier = TenantUserNotifier(
            NotificationScene.USER_INITIALIZE, data_source_id=data_source.id, tenant_id=data_source.owner_tenant_id
        )
        user = TenantUser.objects.filter(tenant_id=data_source.owner_tenant_id).first()
        context_generator = UserTmplContextGenerator(user, NotificationScene.USER_INITIALIZE, passwd="123456")
        tmpl = "{{ username }}, {{ full_name }}, {{ password }}, {{ url }}"
        assert (
            notifier._render_tmpl(tmpl, context_generator)
            == f"{user.data_source_user.username}, {user.data_source_user.full_name}, 123456, {settings.BK_USER_URL}/personal-center"  # noqa: E501
        )

    def test_get_templates(self, data_source):
        notifier = TenantUserNotifier(NotificationScene.MANAGER_RESET_PASSWORD, tenant_id=data_source.owner_tenant_id)
        assert len(notifier.templates) == 1  # noqa: PLR2004

    def test_get_templates_from_plugin_config(self, data_source):
        notifier = TenantUserNotifier(
            NotificationScene.USER_INITIALIZE, data_source_id=data_source.id, tenant_id=data_source.owner_tenant_id
        )
        assert len(notifier.templates) == 2  # noqa: PLR2004

    @mock.patch("bkuser.component.cmsi.BkEsbCmsiClient.send_mail", return_value=None)
    @mock.patch("bkuser.component.cmsi.BkEsbCmsiClient.send_sms", return_value=None)
    def test_batch_send_with_esb(self, mocked_send_sms, mocked_send_mail, data_source):
        notifier = TenantUserNotifier(
            scene=NotificationScene.USER_INITIALIZE,
            data_source_id=data_source.id,
            tenant_id=data_source.owner_tenant_id,
        )
        tenant_users = TenantUser.objects.filter(tenant_id=data_source.owner_tenant_id)
        notifier.batch_send(tenant_users, user_passwd_map={u.data_source_user_id: "123456" for u in tenant_users})

    @mock.patch("bkuser.component.cmsi.BkApigwCmsiClient.send_mail", return_value=None)
    @mock.patch("bkuser.component.cmsi.BkApigwCmsiClient.send_sms", return_value=None)
    def test_batch_send_with_apigw(self, mocked_send_sms, mocked_send_mail, data_source):
        with override_settings(ENABLE_MULTI_TENANT_MODE=True):
            notifier = TenantUserNotifier(
                scene=NotificationScene.USER_INITIALIZE,
                data_source_id=data_source.id,
                tenant_id=data_source.owner_tenant_id,
            )
            tenant_users = TenantUser.objects.filter(tenant_id=data_source.owner_tenant_id)
            notifier.batch_send(tenant_users, user_passwd_map={u.data_source_user_id: "123456" for u in tenant_users})

        with override_settings(HAS_BK_CMSI_APIGW=True):
            notifier = TenantUserNotifier(
                scene=NotificationScene.USER_INITIALIZE,
                data_source_id=data_source.id,
                tenant_id=data_source.owner_tenant_id,
            )
            tenant_users = TenantUser.objects.filter(tenant_id=data_source.owner_tenant_id)
            notifier.batch_send(tenant_users, user_passwd_map={u.data_source_user_id: "123456" for u in tenant_users})

    @mock.patch("bkuser.component.cmsi.BkEsbCmsiClient.send_mail", return_value=None)
    @mock.patch("bkuser.component.cmsi.BkEsbCmsiClient.send_sms", return_value=None)
    def test_send_with_esb(self, mocked_send_sms, mocked_send_mail, data_source):
        notifier = TenantUserNotifier(
            scene=NotificationScene.MANAGER_RESET_PASSWORD, tenant_id=data_source.owner_tenant_id
        )
        tenant_user = TenantUser.objects.filter(tenant_id=data_source.owner_tenant_id).first()
        notifier.send(tenant_user, passwd="123456")

    @mock.patch("bkuser.component.cmsi.BkApigwCmsiClient.send_mail", return_value=None)
    @mock.patch("bkuser.component.cmsi.BkApigwCmsiClient.send_sms", return_value=None)
    def test_send_with_apigw(self, mocked_send_sms, mocked_send_mail, data_source):
        with override_settings(ENABLE_MULTI_TENANT_MODE=True):
            notifier = TenantUserNotifier(
                scene=NotificationScene.MANAGER_RESET_PASSWORD, tenant_id=data_source.owner_tenant_id
            )
            tenant_user = TenantUser.objects.filter(tenant_id=data_source.owner_tenant_id).first()
            notifier.send(tenant_user, passwd="123456")

        with override_settings(HAS_BK_CMSI_APIGW=True):
            notifier = TenantUserNotifier(
                scene=NotificationScene.MANAGER_RESET_PASSWORD, tenant_id=data_source.owner_tenant_id
            )
            tenant_user = TenantUser.objects.filter(tenant_id=data_source.owner_tenant_id).first()
            notifier.send(tenant_user, passwd="123456")


class TestContactNotifier:
    """测试联系方式通知功能"""

    @pytest.fixture
    def data_source(self, random_tenant, full_local_data_source):
        sync_users_depts_to_tenant(random_tenant, full_local_data_source)
        return full_local_data_source

    @mock.patch("bkuser.component.cmsi.BkApigwCmsiClient.send_mail", return_value=None)
    @mock.patch("bkuser.component.cmsi.BkApigwCmsiClient.send_sms", return_value=None)
    def test_send_with_apigw(self, mocked_send_sms, mocked_send_mail, data_source):
        with override_settings(ENABLE_MULTI_TENANT_MODE=True):
            notifier = ContactNotifier(
                scene=NotificationScene.SEND_VERIFICATION_CODE,
                method=NotificationMethod.EMAIL,
                tenant_id=data_source.owner_tenant_id,
            )
            notifier.send(email="test@test.com", verification_code="123456")

        with override_settings(HAS_BK_CMSI_APIGW=True):
            notifier = ContactNotifier(
                scene=NotificationScene.SEND_VERIFICATION_CODE,
                method=NotificationMethod.SMS,
                tenant_id=data_source.owner_tenant_id,
            )
            notifier.send(phone="12345678901", phone_country_code="86", verification_code="123456")

        with override_settings(ENABLE_MULTI_TENANT_MODE=True):
            notifier = ContactNotifier(
                scene=NotificationScene.RESET_PASSWORD,
                tenant_id=data_source.owner_tenant_id,
                data_source_id=data_source.id,
            )
            notifier.send(email="test@test.com", token="123456")
