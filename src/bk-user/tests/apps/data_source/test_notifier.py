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
from unittest import mock

import pytest
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.data_source.notifier import LocalDataSourceUserNotifier
from bkuser.plugins.local.constants import NotificationScene
from django.conf import settings

pytestmark = pytest.mark.django_db


class TestLocalDataSourceUserNotifier:
    """测试本地数据源用户通知功能"""

    def test_render_tmpl_user_initialize(self, full_local_data_source):
        notifier = LocalDataSourceUserNotifier(
            data_source=full_local_data_source, scene=NotificationScene.USER_INITIALIZE
        )
        user = DataSourceUser.objects.filter(data_source=full_local_data_source).first()
        tmpl = "{{ username }}, {{ full_name }}, {{ password }}, {{ reset_url }}"
        assert (
            notifier._render_tmpl(user, tmpl, passwd="123456")
            == f"{user.username}, {user.full_name}, 123456, {settings.BK_USER_URL}/reset-password"
        )

    def test_filter_templates(self, full_local_data_source):
        notifier = LocalDataSourceUserNotifier(
            data_source=full_local_data_source, scene=NotificationScene.USER_INITIALIZE
        )
        assert len(notifier.templates) == 2  # noqa: PLR2004

    def test_send_without_passwd_map(self, full_local_data_source):
        notifier = LocalDataSourceUserNotifier(
            data_source=full_local_data_source, scene=NotificationScene.USER_INITIALIZE
        )
        with pytest.raises(ValueError, match="not found in user passwd map"):
            notifier.send(DataSourceUser.objects.filter(data_source=full_local_data_source))

    @mock.patch("bkuser.component.cmsi.send_mail", return_value=None)
    @mock.patch("bkuser.component.cmsi.send_sms", return_value=None)
    def test_send(self, mocked_send_sms, mocked_send_mail, full_local_data_source):
        notifier = LocalDataSourceUserNotifier(
            data_source=full_local_data_source, scene=NotificationScene.USER_INITIALIZE
        )
        users = DataSourceUser.objects.filter(data_source=full_local_data_source)
        notifier.send(users, user_passwd_map={u.id: "123456" for u in users})
