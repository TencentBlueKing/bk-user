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
from bkuser.apps.notification.constants import NotificationScene
from bkuser.apps.notification.notifier import TenantUserNotifier
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
        notifier = TenantUserNotifier(NotificationScene.USER_INITIALIZE, data_source_id=data_source.id)
        user = TenantUser.objects.filter(tenant_id=data_source.owner_tenant_id).first()
        tmpl = "{{ username }}, {{ full_name }}, {{ password }}, {{ url }}"
        assert (
            notifier._render_tmpl(user, tmpl, passwd="123456")
            == f"{user.data_source_user.username}, {user.data_source_user.full_name}, 123456, {settings.BK_USER_URL}/personal-center"  # noqa: E501
        )

    def test_get_templates(self):
        notifier = TenantUserNotifier(NotificationScene.MANAGER_RESET_PASSWORD)
        assert len(notifier.templates) == 1  # noqa: PLR2004

    def test_get_templates_from_plugin_config(self, data_source):
        notifier = TenantUserNotifier(NotificationScene.USER_INITIALIZE, data_source_id=data_source.id)
        assert len(notifier.templates) == 2  # noqa: PLR2004

    @mock.patch("bkuser.component.clients.BkEsbCmsiClient.send_mail", return_value=None)
    @mock.patch("bkuser.component.clients.BkEsbCmsiClient.send_sms", return_value=None)
    def test_batch_send_with_esb(self, mocked_send_sms, mocked_send_mail, data_source):
        notifier = TenantUserNotifier(scene=NotificationScene.USER_INITIALIZE, data_source_id=data_source.id)
        tenant_users = TenantUser.objects.filter(tenant_id=data_source.owner_tenant_id)
        contact_infos = {
            user.id: {
                "phone_info": {"phone": user.phone_info[0], "phone_country_code": user.phone_info[1]},
                "email": user.email,
            }
            for user in tenant_users
        }
        notifier.batch_send(
            tenant_users, contact_infos, user_passwd_map={u.data_source_user_id: "123456" for u in tenant_users}
        )

    @mock.patch("bkuser.component.clients.BkApigwCmsiClient.send_mail", return_value=None)
    @mock.patch("bkuser.component.clients.BkApigwCmsiClient.send_sms", return_value=None)
    def test_batch_send_with_apigw(self, mocked_send_sms, mocked_send_mail, data_source):
        with override_settings(ENABLE_MUTIL_TENANT_MODE=True):
            notifier = TenantUserNotifier(scene=NotificationScene.USER_INITIALIZE, data_source_id=data_source.id)
            tenant_users = TenantUser.objects.filter(tenant_id=data_source.owner_tenant_id)
            contact_infos = {
                user.id: {
                    "phone_info": {"phone": user.phone_info[0], "phone_country_code": user.phone_info[1]},
                    "email": user.email,
                }
                for user in tenant_users
            }
            notifier.batch_send(
                tenant_users, contact_infos, user_passwd_map={u.data_source_user_id: "123456" for u in tenant_users}
            )

        with override_settings(HAS_BK_CMSI_APIGW=True):
            notifier = TenantUserNotifier(scene=NotificationScene.USER_INITIALIZE, data_source_id=data_source.id)
            tenant_users = TenantUser.objects.filter(tenant_id=data_source.owner_tenant_id)
            contact_infos = {
                user.id: {
                    "phone_info": {"phone": user.phone_info[0], "phone_country_code": user.phone_info[1]},
                    "email": user.email,
                }
                for user in tenant_users
            }
            notifier.batch_send(
                tenant_users, contact_infos, user_passwd_map={u.data_source_user_id: "123456" for u in tenant_users}
            )

    @mock.patch("bkuser.component.clients.BkEsbCmsiClient.send_mail", return_value=None)
    @mock.patch("bkuser.component.clients.BkEsbCmsiClient.send_sms", return_value=None)
    def test_send_with_esb(self, mocked_send_sms, mocked_send_mail, data_source):
        notifier = TenantUserNotifier(scene=NotificationScene.MANAGER_RESET_PASSWORD)
        tenant_user = TenantUser.objects.filter(tenant_id=data_source.owner_tenant_id).first()
        notifier.send(tenant_user, {"email": tenant_user.email}, passwd="123456")

    @mock.patch("bkuser.component.clients.BkApigwCmsiClient.send_mail", return_value=None)
    @mock.patch("bkuser.component.clients.BkApigwCmsiClient.send_sms", return_value=None)
    def test_send_with_apigw(self, mocked_send_sms, mocked_send_mail, data_source):
        with override_settings(ENABLE_MUTIL_TENANT_MODE=True):
            notifier = TenantUserNotifier(scene=NotificationScene.MANAGER_RESET_PASSWORD)
            tenant_user = TenantUser.objects.filter(tenant_id=data_source.owner_tenant_id).first()
            notifier.send(tenant_user, {"email": tenant_user.email}, passwd="123456")

        with override_settings(HAS_BK_CMSI_APIGW=True):
            notifier = TenantUserNotifier(scene=NotificationScene.MANAGER_RESET_PASSWORD)
            tenant_user = TenantUser.objects.filter(tenant_id=data_source.owner_tenant_id).first()
            notifier.send(tenant_user, {"email": tenant_user.email}, passwd="123456")
