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
from bkuser.apps.notification.constants import VerificationCodeScene
from bkuser.apps.notification.exceptions import ExceedSendVerificationCodeLimit, ExceedVerificationCodeRetries
from bkuser.apps.notification.verification_code import VerificationCodeManager
from bkuser.apps.tenant.models import TenantUser
from django.conf import settings

from tests.test_utils.tenant import sync_users_depts_to_tenant

pytestmark = pytest.mark.django_db


@pytest.fixture()
def tenant_user(default_tenant, full_local_data_source) -> TenantUser:
    sync_users_depts_to_tenant(default_tenant, full_local_data_source)
    return TenantUser.objects.filter(data_source_id=full_local_data_source.id).first()


@pytest.fixture()
def vc_mgr(tenant_user) -> VerificationCodeManager:
    return VerificationCodeManager(tenant_user, VerificationCodeScene.RESET_PASSWORD)


class TestVerificationCodeManager:
    def test_validate(self, vc_mgr):
        code = vc_mgr._get_verification_code()
        vc_mgr.validate(code)

    def test_validate_with_too_many_retries(self, vc_mgr):
        code = vc_mgr._get_verification_code()
        # 过多次数的失败尝试也会导致验证码失效
        for _ in range(settings.VERIFICATION_CODE_MAX_RETRIES):
            try:
                vc_mgr.validate(f"fake-{code}")
            except Exception:  # noqa: PERF203
                pass

        with pytest.raises(ExceedVerificationCodeRetries):
            vc_mgr.validate(code)

    def test_too_many_send(self, vc_mgr):
        with pytest.raises(ExceedSendVerificationCodeLimit):  # noqa: PT012
            for _ in range(settings.VERIFICATION_CODE_MAX_SEND_PER_DAY + 1):
                vc_mgr.send()
