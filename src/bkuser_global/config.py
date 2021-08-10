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
import os

import environ


def init_patch():
    import pymysql
    import urllib3

    # no more useless warning

    urllib3.disable_warnings()

    # ==============================================================================
    # Patching
    # ==============================================================================
    pymysql.install_as_MySQLdb()
    # Patch version info to forcely pass Django client check
    setattr(pymysql, "version_info", (1, 4, 6, "final", 0))


def get_db_config(env: environ.Env, db_prefix: str) -> dict:
    """通用 DB 配置获取方法"""
    return {
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


def get_logging_config_dict(log_level: str, logging_dir: str, log_class: str, file_name: str, package_name: str):
    if not os.path.exists(logging_dir):
        os.makedirs(logging_dir)

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "%(levelname)s [%(asctime)s] %(name)s(ln:%(lineno)d): %(message)s",  # noqa
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {"format": "%(levelname)s %(message)s"},
            "iam": {"format": "[IAM] %(asctime)s %(message)s"},
        },
        "handlers": {
            "null": {"level": "DEBUG", "class": "logging.NullHandler"},
            "root": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(logging_dir, "%s.log" % file_name),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
            },
            "console": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
            "component": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(logging_dir, "component.log"),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
            },
            "iam": {
                "class": log_class,
                "formatter": "iam",
                "filename": os.path.join(logging_dir, "iam.log"),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
            },
        },
        "loggers": {
            "django": {
                "handlers": ["null"],
                "level": "INFO",
                "propagate": True,
            },
            "django.request": {
                "handlers": [
                    "root",
                ],
                "level": "ERROR",
                "propagate": True,
            },
            "django.db.backends": {
                "handlers": [
                    "root",
                ],
                "level": "INFO",
                "propagate": True,
            },
            "django.security": {
                "handlers": [
                    "root",
                ],
                "level": "INFO",
                "propagate": True,
            },
            package_name: {
                "handlers": [
                    "console",
                ],
                "level": log_level,
                "propagate": True,
            },
            "root": {
                "handlers": [
                    "console",
                ],
                "level": log_level,
                "propagate": True,
            },
            "requests": {
                "handlers": [
                    "console",
                ],
                "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            },
            # 组件调用日志
            "component": {
                "handlers": ["console"],
                "level": "WARN",
                "propagate": True,
            },
            "iam": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": True,
            },
        },
    }
