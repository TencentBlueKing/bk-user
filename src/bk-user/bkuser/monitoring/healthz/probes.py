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
from blue_krill.monitoring.probe.mysql import MySQLProbe, transfer_django_db_settings
from django.conf import settings
from django.utils.module_loading import import_string


def get_default_probes():
    return [import_string(p) for p in settings.HEALTHZ_PROBES]


class MysqlProbe(MySQLProbe):
    name = "bkuser-mysql"
    config = transfer_django_db_settings(settings.DATABASES["default"])
