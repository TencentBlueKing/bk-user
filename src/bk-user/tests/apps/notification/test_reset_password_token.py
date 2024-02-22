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
from bkuser.apps.notification.constants import TokenRelatedObjType
from bkuser.apps.notification.exceptions import ExceedSendResetPasswordTokenLimit
from bkuser.apps.notification.reset_passwd_token import UserResetPasswordTokenManager
from django.conf import settings

pytestmark = pytest.mark.django_db


class TestUserResetPasswordTokenManager:
    @pytest.mark.parametrize(
        "related_obj_type",
        [
            TokenRelatedObjType.TENANT_USER,
            TokenRelatedObjType.EMAIL,
            TokenRelatedObjType.PHONE,
        ],
    )
    def test_gen_token_and_list_user(self, tenant_user, related_obj_type):
        mgr = UserResetPasswordTokenManager()
        token = mgr.gen_token(tenant_user, related_obj_type)

        assert mgr.list_users_by_token(token).filter(id=tenant_user.id).exists()

    def test_too_many_send(self, tenant_user):
        mgr = UserResetPasswordTokenManager()
        with pytest.raises(ExceedSendResetPasswordTokenLimit):  # noqa: PT012
            for _ in range(settings.RESET_PASSWORD_TOKEN_MAX_SEND_PER_DAY + 1):
                mgr.send(tenant_user)
