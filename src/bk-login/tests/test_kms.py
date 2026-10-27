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
import json
import os
import sys
import types
from typing import Any, Dict

import pytest
from bklogin import kms
from django.core.exceptions import ImproperlyConfigured


class _CryptoError(Exception):
    pass


class _CryptoBackendUnavailableError(_CryptoError):
    pass


def _install_sdk(monkeypatch, plaintext: str) -> types.SimpleNamespace:
    def decrypt(*, envelope: str, private_key: str) -> str:
        assert envelope == "envelope-body"
        assert private_key == "private-key"
        return plaintext

    sdk = types.SimpleNamespace(
        CryptoError=_CryptoError,
        CryptoBackendUnavailableError=_CryptoBackendUnavailableError,
        decrypt=decrypt,
    )
    monkeypatch.setitem(sys.modules, "bk_kms", sdk)
    return sdk


def _enable(monkeypatch, tmp_path, credentials: Dict[str, Any] | str) -> types.SimpleNamespace:
    envelope = tmp_path / "envelope"
    envelope.write_text("envelope-body\n", encoding="utf-8")
    monkeypatch.setattr(kms, "KMS_ENVELOPE_PATH", envelope)
    monkeypatch.setenv("ENABLE_KMS", "true")
    monkeypatch.setenv("BK_USER_KMS_PRIVATE_KEY", "private-key\n")

    plaintext = credentials if isinstance(credentials, str) else json.dumps(credentials)
    return _install_sdk(monkeypatch, plaintext)


def _credentials() -> Dict[str, Any]:
    return {
        "bkapp_id_secret": {
            "bkuser": {"app_code": "bk_usermgr", "app_secret": "user-app-secret"},
            "bklogin": {"app_code": "bk_login", "app_secret": "$login-app-secret"},
        },
        "mysql": {
            "bkuser": {"username": "bkuser", "password": "user-mysql-password"},
            "bklogin": {"username": "bklogin", "password": "login-mysql-password"},
        },
        "tokens": {
            "bkuser": {"apigateway_inner": {"token": "user-inner-token"}},
            "bklogin": {"apigateway_inner": {"token": "login-inner-token"}},
        },
        "encryption": {
            "bkuser": {"bkkrill_secret_key": "U" * 43 + "="},
            "bklogin": {"bkkrill_secret_key": "L" * 43 + "="},
        },
    }


def test_disabled_keeps_environment_and_skips_envelope(monkeypatch, tmp_path):
    monkeypatch.delenv("ENABLE_KMS", raising=False)
    monkeypatch.setenv("BK_APP_SECRET", "legacy-secret")
    monkeypatch.setattr(kms, "KMS_ENVELOPE_PATH", tmp_path / "missing")

    env = kms.get_env()

    assert env.str("BK_APP_SECRET") == "legacy-secret"


@pytest.mark.parametrize("flag", ["", "false", "TRUE", " true", "1", "yes"])
def test_only_exact_true_enables_kms(monkeypatch, flag):
    monkeypatch.setenv("ENABLE_KMS", flag)
    monkeypatch.delenv("BK_USER_KMS_PRIVATE_KEY", raising=False)

    env = kms.get_env()

    assert env.str("ENABLE_KMS") == flag


def test_enabled_overrides_bklogin_credentials_without_changing_environment(monkeypatch, tmp_path):
    _enable(monkeypatch, tmp_path, _credentials())
    monkeypatch.setenv("BK_APP_SECRET", "legacy-secret")
    monkeypatch.setenv("MYSQL_HOST", "mysql.internal")

    env = kms.get_env()

    assert env.str("BK_APP_CODE") == "bk_login"
    assert env.str("BK_APP_SECRET") == "$login-app-secret"
    assert env.str("BK_USER_APP_CODE") == "bk_usermgr"
    assert env.str("BK_USER_APP_SECRET") == "user-app-secret"
    assert env.str("MYSQL_USER") == "bklogin"
    assert env.str("MYSQL_PASSWORD") == "login-mysql-password"
    assert env.str("BK_APIGW_TO_BK_USER_INNER_BEARER_TOKEN") == "login-inner-token"
    assert env.str("BKKRILL_ENCRYPT_SECRET_KEY") == "L" * 43 + "="
    assert env.str("MYSQL_HOST") == "mysql.internal"
    assert os.environ["BK_APP_SECRET"] == "legacy-secret"


@pytest.mark.parametrize(
    "path",
    [
        ("bkapp_id_secret", "bklogin", "app_secret"),
        ("bkapp_id_secret", "bkuser", "app_secret"),
        ("mysql", "bklogin", "password"),
        ("tokens", "bklogin", "apigateway_inner", "token"),
        ("encryption", "bklogin", "bkkrill_secret_key"),
    ],
)
def test_blank_required_field_fails_closed(monkeypatch, tmp_path, path):
    credentials = _credentials()
    cursor = credentials
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = "  "
    _enable(monkeypatch, tmp_path, credentials)

    with pytest.raises(ImproperlyConfigured, match=r"\.".join(path)):
        kms.get_env()


def test_missing_private_key_fails(monkeypatch):
    monkeypatch.setenv("ENABLE_KMS", "true")
    monkeypatch.delenv("BK_USER_KMS_PRIVATE_KEY", raising=False)

    with pytest.raises(ImproperlyConfigured, match="BK_USER_KMS_PRIVATE_KEY"):
        kms.get_env()


def test_decrypt_error_hides_sdk_message(monkeypatch, tmp_path):
    sdk = _enable(monkeypatch, tmp_path, "unused")

    def decrypt(*, envelope: str, private_key: str) -> str:
        raise _CryptoError("plaintext-password")

    sdk.decrypt = decrypt

    with pytest.raises(ImproperlyConfigured, match="Unable to decode or decrypt") as exc_info:
        kms.get_env()

    assert "plaintext-password" not in str(exc_info.value)
