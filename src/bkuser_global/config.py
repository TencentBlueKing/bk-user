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
import environ


def init_patch():
    import pymysql
    import urllib3

    # 禁用不必要的警告
    urllib3.disable_warnings()

    # ==============================================================================
    # Patching
    # ==============================================================================
    pymysql.install_as_MySQLdb()


def get_db_config(env: environ.Env, db_prefix: str) -> dict:
    """通用 DB 配置获取方法"""
    cfg = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env(f"{db_prefix}_NAME"),
            "USER": env(f"{db_prefix}_USER"),
            "PASSWORD": env(f"{db_prefix}_PASSWORD"),
            "HOST": env(f"{db_prefix}_HOST"),
            "PORT": env(f"{db_prefix}_PORT"),
            "OPTIONS": {"charset": "utf8mb4"},
            "TEST": {"CHARSET": "utf8mb4", "COLLATION": "utf8mb4_general_ci"},
        }
    }
    tls_enabled = env.bool(f"{db_prefix}_TLS_ENABLED", default=False)
    tls_ca = env.str(f"{db_prefix}_TLS_CERT_CA_FILE", default="")
    tls_cert = env.str(f"{db_prefix}_TLS_CERT_FILE", default="")
    tls_key = env.str(f"{db_prefix}_TLS_CERT_KEY_FILE", default="")
    # 跳过主机名/IP 验证，会降低安全性，正式环境需要设置为 True
    tls_check_hostname = env.bool(f"{db_prefix}_TLS_CHECK_HOSTNAME", default=True)
    if tls_enabled:
        cfg["default"]["OPTIONS"]["ssl"] = {"ca": tls_ca, "check_hostname": tls_check_hostname}
        # mTLS
        if tls_cert and tls_key:
            cfg["default"]["OPTIONS"]["ssl"]["cert"] = tls_cert
            cfg["default"]["OPTIONS"]["ssl"]["key"] = tls_key

    return cfg
