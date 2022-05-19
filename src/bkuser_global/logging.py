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
import logging
import os

from .local import local


class RequestIDFilter(logging.Filter):
    """
    request id log filter
    日志记录中增加request id
    """

    def filter(self, record):
        record.request_id = local.request_id
        return True


class LoggingType:
    """日志输出类型"""

    # 所有日志都送到标注输出，对于容器部署时更亲和
    STDOUT = 0
    # 日志按类型分散在各个不同文件，二进制部署时更亲和
    FILE = 1


def get_logging(logging_type: int, **kwargs) -> dict:
    """获取 Logging 配置"""

    if logging_type == LoggingType.STDOUT:
        return get_stdout_logging(**kwargs)
    elif logging_type == LoggingType.FILE:
        return get_file_logging(**kwargs)
    else:
        return get_file_logging(**kwargs)


formatters = {
    "verbose": {
        "format": "%(levelname)s [%(asctime)s] %(lineno)d %(funcName)s %(process)d %(thread)d \n%(message)s \n",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    },
    "json": {
        "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
        "fmt": (
            "%(levelname)s %(asctime)s %(pathname)s %(lineno)d "
            "%(funcName)s %(process)d %(thread)d %(request_id)s %(message)s"
        ),
    },
    "simple": {"format": "%(levelname)s [%(asctime)s] %(message)s"},
    "iam": {"format": "[IAM] %(levelname)s [%(asctime)s] %(message)s"},
}


def get_loggers(package_name: str, log_level: str) -> dict:
    return {
        "django": {
            "handlers": ["null"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["root"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["root"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["root"],
            "level": "INFO",
            "propagate": False,
        },
        package_name: {
            "handlers": ["root"],
            "level": log_level,
            "propagate": False,
        },
        "": {
            "handlers": ["root"],
            "level": log_level,
        },
        "requests": {
            "handlers": ["root"],
            "level": log_level,
            "propagate": False,
        },
        # 组件调用日志
        "component": {
            "handlers": ["root"],
            "level": "WARN",
            "propagate": False,
        },
        "iam": {
            "handlers": ["root"],
            "level": log_level,
            "propagate": False,
        },
    }


def get_stdout_logging(log_level: str, package_name: str, formatter: str = "json"):
    """获取标准输出日志配置"""
    log_class = "logging.StreamHandler"

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_id_filter": {
                "()": RequestIDFilter,
            }
        },
        "formatters": formatters,
        "handlers": {
            "null": {"level": "DEBUG", "class": "logging.NullHandler"},
            "root": {
                "class": log_class,
                "formatter": formatter,
                "filters": ["request_id_filter"],
            },
            "component": {
                "class": log_class,
                "formatter": formatter,
                "filters": ["request_id_filter"],
            },
            "iam": {
                "class": log_class,
                "formatter": "iam",
                "filters": ["request_id_filter"],
            },
        },
        "loggers": get_loggers(package_name, log_level),
    }


def get_file_logging(log_level: str, logging_dir: str, file_name: str, package_name: str, formatter: str = "json"):
    """获取文件日志配置"""
    log_class = "logging.handlers.RotatingFileHandler"

    if not os.path.exists(logging_dir):
        os.makedirs(logging_dir)

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_id_filter": {
                "()": RequestIDFilter,
            }
        },
        "formatters": formatters,
        "handlers": {
            "null": {"level": "DEBUG", "class": "logging.NullHandler"},
            "root": {
                "class": log_class,
                "formatter": formatter,
                "filename": os.path.join(logging_dir, f"{file_name}.log"),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
                "filters": ["request_id_filter"],
            },
            "component": {
                "class": log_class,
                "formatter": formatter,
                "filename": os.path.join(logging_dir, "component.log"),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
                "filters": ["request_id_filter"],
            },
            "iam": {
                "class": log_class,
                "formatter": "iam",
                "filename": os.path.join(logging_dir, "iam.log"),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
                "filters": ["request_id_filter"],
            },
        },
        "loggers": get_loggers(package_name, log_level),
    }
