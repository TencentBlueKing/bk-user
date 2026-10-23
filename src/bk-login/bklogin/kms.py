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
"""Load deployment credentials from the KMS envelope before Django settings are evaluated."""

import json
import os
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

# bkuser and bklogin share one envelope and private key; credentials are grouped by service name inside it.
KMS_ENVELOPE_PATH = Path("/etc/secrets/bk-user-kms")
KMS_PRIVATE_KEY_ENV = "BK_USER_KMS_PRIVATE_KEY"


class _KMSEnv(environ.Env):
    """Environment reader that prefers decrypted credentials.

    Credential strings are literal, including a leading ``$``. django-environ must
    not interpret them as references to other variables.
    """

    def __init__(self, credentials: dict[str, str]):
        super().__init__()
        self._credentials = credentials

    def get_value(self, var, cast=None, default=environ.Env.NOTSET, parse_default=False):
        if var in self._credentials:
            return self.parse_value(self._credentials[var], cast)
        return super().get_value(var, cast=cast, default=default, parse_default=parse_default)


def _credential_bindings() -> dict[str, tuple[str, ...]]:
    return {
        "BK_APP_CODE": ("bkapp_id_secret", "bklogin", "app_code"),
        "BK_APP_SECRET": ("bkapp_id_secret", "bklogin", "app_secret"),
        # bklogin calls bk-user APIs with bk-user's own app identity.
        "BK_USER_APP_CODE": ("bkapp_id_secret", "bkuser", "app_code"),
        "BK_USER_APP_SECRET": ("bkapp_id_secret", "bkuser", "app_secret"),
        "MYSQL_USER": ("mysql", "bklogin", "username"),
        "MYSQL_PASSWORD": ("mysql", "bklogin", "password"),
        "BK_APIGW_TO_BK_USER_INNER_BEARER_TOKEN": ("tokens", "bklogin", "apigateway_inner", "token"),
        "BKKRILL_ENCRYPT_SECRET_KEY": ("encryption", "bklogin", "bkkrill_secret_key"),
    }


def is_kms_enabled() -> bool:
    return os.environ.get("ENABLE_KMS") in ("true", "True")


def _load_kms_credentials(private_key: str) -> object:
    """Read, decrypt and parse credentials with sanitized errors for each stage."""
    try:
        from bk_kms import CryptoBackendUnavailableError, CryptoError, decrypt
    except ImportError:
        raise ImproperlyConfigured("KMS requires the bk-kms-sdk package") from None

    try:
        envelope = KMS_ENVELOPE_PATH.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ImproperlyConfigured(
            f"Unable to read KMS credential envelope file {KMS_ENVELOPE_PATH}: "
            f"{type(exc).__name__} (errno={exc.errno}); check the file mount and read permissions"
        ) from None
    except UnicodeError:
        raise ImproperlyConfigured(f"KMS credential envelope file {KMS_ENVELOPE_PATH} is not valid UTF-8") from None

    try:
        plaintext = decrypt(envelope=envelope, private_key=private_key)
    except CryptoBackendUnavailableError:
        raise ImproperlyConfigured(
            "KMS SM2/SM4 crypto backend is unavailable; check the installed gm dependencies and native libraries"
        ) from None
    except UnicodeError:
        raise ImproperlyConfigured(
            "KMS credential envelope decoding or decryption failed with an encoding error"
        ) from None
    except (OSError, ValueError, CryptoError) as exc:
        # SDK errors can wrap credential text. Keep the cause type check, never its message.
        if isinstance(exc.__cause__, UnicodeError):
            raise ImproperlyConfigured(
                "KMS credential envelope decoding or decryption failed with an encoding error"
            ) from None
        raise ImproperlyConfigured(
            "Unable to decode or decrypt the KMS credential envelope; "
            "check the envelope format, private key format and whether the key matches the envelope"
        ) from None

    try:
        return json.loads(plaintext)
    except json.JSONDecodeError as exc:
        raise ImproperlyConfigured(
            "KMS credential envelope decrypted successfully but is not valid JSON: "
            f"{exc.msg} (line {exc.lineno}, column {exc.colno}, char {exc.pos})"
        ) from None
    except ValueError:
        raise ImproperlyConfigured(
            "KMS credential envelope decrypted successfully but contains an unsupported JSON value"
        ) from None


def get_env() -> environ.Env:
    """Return the original env when disabled; fail closed for required KMS fields."""
    env = environ.Env()
    if not is_kms_enabled():
        return env

    private_key = os.environ.get(KMS_PRIVATE_KEY_ENV, "").strip()
    if not private_key:
        raise ImproperlyConfigured(f"KMS requires {KMS_PRIVATE_KEY_ENV}")

    credentials = _load_kms_credentials(private_key)

    values = {}
    for name, path in _credential_bindings().items():
        value = credentials
        for part in path:
            value = value.get(part) if isinstance(value, dict) else None
        if not isinstance(value, str) or not value.strip():
            raise ImproperlyConfigured(f"KMS requires a non-empty string at {'.'.join(path)}")
        values[name] = value

    return _KMSEnv(values)
