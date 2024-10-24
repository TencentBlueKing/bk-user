# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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
import datetime

import pytest
from bkuser.apps.data_source.models import DataSourceUserDeprecatedPasswordRecord, LocalDataSourceIdentityInfo
from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.validators import validate_logo, validate_user_new_password
from bkuser.common.constants import PERMANENT_TIME
from bkuser.common.hashers import make_password
from bkuser.common.passwd import PasswordGenerator
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig
from django.utils import timezone
from rest_framework.exceptions import ValidationError

pytestmark = pytest.mark.django_db


class TestValidateUserNewPassword:
    @pytest.fixture(autouse=True)
    def _initialize(self, bk_user):
        tenant_user = TenantUser.objects.get(id=bk_user.username)

        self.data_source_user_id = tenant_user.data_source_user_id

        data_source = tenant_user.data_source
        assert data_source.plugin_id == DataSourcePluginEnum.LOCAL
        self.data_source_config = data_source.get_plugin_cfg()
        assert isinstance(self.data_source_config, LocalDataSourcePluginConfig)
        assert self.data_source_config.password_rule is not None
        assert self.data_source_config.password_expire is not None

        # 初始化密码(或直接更新掉密码，便于后面测试)
        password_generator = PasswordGenerator(self.data_source_config.password_rule.to_rule())
        self.current_password = password_generator.generate()
        encrypted_password = make_password(self.current_password)
        time_now = timezone.now()
        expired_at = (
            PERMANENT_TIME
            if self.data_source_config.password_expire.valid_time < 0
            else time_now + datetime.timedelta(days=self.data_source_config.password_expire.valid_time)
        )

        LocalDataSourceIdentityInfo.objects.update_or_create(
            user=tenant_user.data_source_user,
            defaults={
                "data_source": data_source,
                "username": tenant_user.data_source_user.username,
                "password": encrypted_password,
                "password_updated_at": time_now,
                "password_expired_at": expired_at,
            },
        )

        # 同时生成前 n 次密码，用于测试
        self.deprecated_raw_passwords = [password_generator.generate() for _ in range(5)]
        DataSourceUserDeprecatedPasswordRecord.objects.bulk_create(
            [
                DataSourceUserDeprecatedPasswordRecord(
                    user=tenant_user.data_source_user, password=make_password(p), operator="admin"
                )
                for index, p in enumerate(self.deprecated_raw_passwords)
            ]
        )
        self.deprecated_raw_passwords.reverse()

    def test_not_match_password_rule(self):
        """注意，这里不重点测试规则本身"""
        with pytest.raises(ValidationError) as error:
            validate_user_new_password("12345678", self.data_source_user_id, self.data_source_config)

        assert "密码不符合规则" in str(error.value)

    def test_allow_duplicate_password(self):
        self.data_source_config.password_initial.cannot_use_previous_password = False

        new_password = self.current_password

        assert new_password == validate_user_new_password(
            new_password, self.data_source_user_id, self.data_source_config
        )

    def test_not_allow_duplicate_current_password(self):
        self.data_source_config.password_initial.cannot_use_previous_password = True

        with pytest.raises(ValidationError) as error:
            validate_user_new_password(self.current_password, self.data_source_user_id, self.data_source_config)

        assert "新密码不能与当前密码相同" in str(error.value)

    def test_not_allow_duplicate_n_password(self):
        """仅仅不允许与当前密码相同"""
        config = self.data_source_config
        config.password_initial.cannot_use_previous_password = True

        for count in range(5):
            config.password_initial.reserved_previous_password_count = count

            # 只要 cannot_use_previous_password = True，则无论多少次，不允许与当前密码一样
            with pytest.raises(ValidationError) as error:
                validate_user_new_password(self.current_password, self.data_source_user_id, config)

            assert "新密码不能与当前密码相同" in str(error.value)

            # 实际上 0 和 1 都认为一种情况
            if count == 0:
                continue

            # 不允许的相同的密码列表
            for i in self.deprecated_raw_passwords[: count - 1]:
                with pytest.raises(ValidationError) as error:
                    validate_user_new_password(i, self.data_source_user_id, config)

                assert f"新密码不能与近 {count} 次使用的密码相同" in str(error.value)

            # 允许相同的密码列表
            for i in self.deprecated_raw_passwords[count - 1 :]:
                assert i == validate_user_new_password(i, self.data_source_user_id, self.data_source_config)


class TestValidateLogo:
    @pytest.mark.parametrize(
        ("logo_data"),
        [
            (""),
            ("data:image/png;base64,QAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQoMDAsKCwsNDhIQDQ4ERMUFRUVDA8XGBYU"),
            ("data:image/jpeg;base64,QAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQoMDAsKCwsNDhIQDQ4ERMUFRUVDA8XGBYU"),
        ],
    )
    def test_legal_logo_format(self, logo_data):
        assert validate_logo(logo_data) == logo_data

    @pytest.mark.parametrize(
        ("logo_data"),
        [
            ("data:image/gif;base64,QAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQoMDAsKCwsNDhIQDQ4ERMUFRUVDA8XGBYU"),
            ("data:application/zip;base64,QAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQoMDAsKCwsNDhIQDQ4ERMUFRUVDA8XGBYU"),
        ],
    )
    def test_illegal_logo_format(self, logo_data):
        with pytest.raises(ValidationError) as error:
            validate_logo(logo_data)

        assert "Logo 文件只能为 png 或 jpg 格式" in str(error.value)
