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

from bkuser.common.hashers import PBKDF2SM3PasswordHasher

SMALL_ITERATIONS = 3000


class TestPBKDF2SM3PasswordHasher:
    """测试自定义 Hash 实现（pbkdf2 + hmac + sm3）"""

    def test_simple(self, raw_password):
        hasher = PBKDF2SM3PasswordHasher()
        encrypted = hasher.encode(raw_password)

        excepted_keys = {"algorithm", "hash", "iterations", "salt"}
        assert set(hasher.decode(encrypted).keys()) == excepted_keys
        assert set(hasher.safe_summary(encrypted).keys()) == excepted_keys
        assert not hasher.must_update(encrypted)

        assert hasher.verify(raw_password, encrypted)

    def test_with_salt(self, raw_password):
        hasher = PBKDF2SM3PasswordHasher()
        encrypted = hasher.encode(raw_password, salt="this-is-a-salt")

        decoded = hasher.decode(encrypted)
        assert decoded["salt"] == "this-is-a-salt"
        assert decoded["hash"] == "JAZq76l8rPx1hWEX1GSrHAApEmERAfoZbYB/9qzA5m8="

        summary = hasher.safe_summary(encrypted)
        assert summary["salt"] == "this-i********"
        assert summary["hash"] == "JAZq76**************************************"

        assert hasher.verify(raw_password, encrypted)

    def test_with_special_iterations(self, raw_password):
        hasher = PBKDF2SM3PasswordHasher()
        encrypted = hasher.encode(raw_password, iterations=SMALL_ITERATIONS)

        decoded = hasher.decode(encrypted)
        assert decoded["algorithm"] == "pbkdf2_sm3"
        assert decoded["iterations"] == SMALL_ITERATIONS

        summary = hasher.safe_summary(encrypted)
        assert summary["algorithm"] == "pbkdf2_sm3"
        assert summary["iterations"] == SMALL_ITERATIONS

        assert hasher.verify(raw_password, encrypted)

    def test_must_update_short_salt(self, raw_password):
        hasher = PBKDF2SM3PasswordHasher()
        encrypted = hasher.encode(raw_password, salt="salt_v")

        assert hasher.must_update(encrypted)
        hasher.harden_runtime(raw_password, encrypted)

    def test_must_update_small_iterations(self, raw_password):
        hasher = PBKDF2SM3PasswordHasher()

        assert hasher.iterations > SMALL_ITERATIONS
        encrypted = hasher.encode(raw_password, iterations=SMALL_ITERATIONS)

        assert hasher.must_update(encrypted)
        hasher.harden_runtime(raw_password, encrypted)
