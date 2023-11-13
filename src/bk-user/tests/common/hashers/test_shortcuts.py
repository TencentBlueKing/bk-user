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
from bkuser.common.hashers import check_password, make_password
from django.conf import settings
from django.test.utils import override_settings


def test_make_and_check_password_pbkdf2_sha256(raw_password):
    """测试 pbkdf2_sha256 加密 & 验证"""
    assert settings.PASSWORD_ENCRYPT_ALGORITHM == "pbkdf2_sha256"

    encrypted = make_password(raw_password)
    assert encrypted.startswith("pbkdf2_sha256$")
    assert check_password(raw_password, encrypted)


def test_make_and_check_password_pbkdf2_sm3(raw_password):
    """测试 pbkdf2_sm3 加密 & 验证"""
    with override_settings(PASSWORD_ENCRYPT_ALGORITHM="pbkdf2_sm3"):
        encrypted = make_password(raw_password)
        assert encrypted.startswith("pbkdf2_sm3$")
        assert check_password(raw_password, encrypted)


def test_make_and_check_password_pbkdf2_sm3_with_special_salt(raw_password):
    """测试 pbkdf2_sm3 加密 & 验证（特殊指定盐值，加密结果应该是固定的）"""
    with override_settings(PASSWORD_ENCRYPT_ALGORITHM="pbkdf2_sm3"):
        salt = "this-is-a-salt"
        encrypted = make_password(raw_password, salt=salt)
        assert encrypted == "pbkdf2_sm3$26000$this-is-a-salt$JAZq76l8rPx1hWEX1GSrHAApEmERAfoZbYB/9qzA5m8="
        assert check_password(raw_password, encrypted)


def test_check_password_encrypt_by_other_algo_case_1(raw_password):
    """被 pbkdf2_sm3 加密的密码，即使配置指定的 pbkdf2_sha256，也可以验证通过，反之亦然"""
    with override_settings(PASSWORD_ENCRYPT_ALGORITHM="pbkdf2_sm3"):
        encrypted = make_password(raw_password)
        assert encrypted.startswith("pbkdf2_sm3$")

    assert settings.PASSWORD_ENCRYPT_ALGORITHM == "pbkdf2_sha256"
    assert check_password(raw_password, encrypted)


def test_check_password_encrypt_by_other_algo_case_2(raw_password):
    """被 pbkdf2_sm3 加密的密码，即使配置指定的 pbkdf2_sha256，也可以验证通过，反之亦然"""
    encrypted = make_password(raw_password)
    assert encrypted.startswith("pbkdf2_sha256$")

    with override_settings(PASSWORD_ENCRYPT_ALGORITHM="pbkdf2_sm3"):
        assert settings.PASSWORD_ENCRYPT_ALGORITHM == "pbkdf2_sm3"
        assert check_password(raw_password, encrypted)
