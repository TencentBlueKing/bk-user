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
from unittest.mock import patch

import pytest
from bkuser_core.profiles.constants import PASSWD_RESET_VIA_SAAS_EMAIL_TMPL
from bkuser_core.profiles.exceptions import ProfileEmailEmpty
from bkuser_core.profiles.tasks import send_password_by_email
from bkuser_core.tests.utils import make_simple_profile
from bkuser_core.user_settings.models import Setting
from django.conf import settings

pytestmark = pytest.mark.django_db


class TestSendMailTask:
    @pytest.mark.parametrize(
        "profile_id, email, raw_password, init, token, expected",
        [
            (1000, "", "qwer", True, None, ProfileEmailEmpty),
            (1000, "faker@email.com", "qwer", True, None, f"faker:qwer:{settings.LOGIN_REDIRECT_TO}"),
            (1000, "faker@email.com", "qwer", False, None, PASSWD_RESET_VIA_SAAS_EMAIL_TMPL.format(username="faker")),
            (
                1000,
                "faker@email.com",
                "abcd",
                False,
                "aaaa",
                f"{settings.SAAS_URL}set_password?token=aaaa :{settings.SAAS_URL}reset_password ",
            ),
        ],
    )
    def test_send_mail(self, profile_id, email, raw_password, init, token, expected):
        make_simple_profile("faker", force_create_params={"id": profile_id, "email": email})

        with patch("bkuser_core.profiles.tasks.send_mail") as mocked_send_mail:
            fake_email_config = {
                "init_mail_config": {
                    "title": "title",
                    "sender": "faker",
                    "content": "{username}:{password}:{url}",
                },
                "reset_mail_config": {
                    "title": "title",
                    "sender": "faker",
                    "content": "{url}:{reset_url}",
                },
            }
            for k, v in fake_email_config.items():
                s = Setting.objects.get(category_id=1, meta__key=k)
                s.value = v
                s.save()

            if type(expected) is type and issubclass(expected, Exception):
                with pytest.raises(expected):
                    send_password_by_email(profile_id, raw_password, init, token)
            else:
                send_password_by_email(profile_id, raw_password, init, token)
                assert mocked_send_mail.called
                assert mocked_send_mail.call_args[1]["message"] == expected
                assert mocked_send_mail.call_args[1]["receivers"] == [email]

    def test_send_mail_unknown(self):
        with patch("bkuser_core.profiles.tasks.send_mail") as _:
            with pytest.raises(Exception):
                send_password_by_email(2)
