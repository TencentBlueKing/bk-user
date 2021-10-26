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
from django.conf import settings
from django.utils.module_loading import import_string

from .base import HttpProbe, MySQLProbe, RedisProbe


def get_default_probes():
    probe_modules = getattr(settings, "HEALTHZ_PROBES")
    probes = []
    for probe_module in probe_modules:
        probes.append(import_string(probe_module))
    return probes


def transfer_django_db_settings(django_db_settings) -> dict:
    # transfer django db settings to pymysql params style
    return {
        "host": django_db_settings["HOST"],
        "user": django_db_settings["USER"],
        "password": django_db_settings["PASSWORD"],
        "db": django_db_settings["NAME"],
        "port": int(django_db_settings["PORT"]),
    }


class DefaultDBProbe(MySQLProbe):
    name = "default-db"
    mysql_config = transfer_django_db_settings(settings.DATABASES["default"])


class ESBProbe(HttpProbe):
    name = "ESB"
    healthz_check = {
        "url": f"{settings.BK_COMPONENT_API_URL}/esb/healthz/",
        "token": settings.COMMON_HEALTHZ_TOKEN,
    }
    diagnose_method = "make_healthz_check"


class CacheRedis(RedisProbe):
    name = "cache-redis"
    redis_url = settings.REDIS_URL
