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
import logging
from typing import Dict

from bkuser.apps.data_source.constants import USER_EXTRAS_UPDATE_BATCH_SIZE
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.celery import app
from bkuser.common.task import BaseTask
from bkuser.plugins.constants import DataSourcePluginEnum

logger = logging.getLogger(__name__)


@app.task(base=BaseTask, ignore_result=True)
def remove_dropped_field_in_data_source_field_mapping(tenant_id: str, field_name: str):
    """删除租户某个用户自定义字段后，需要将各数据源的 FieldMapping 中的该字段一并清除"""
    data_sources = DataSource.objects.filter(owner_tenant_id=tenant_id).exclude(plugin_id=DataSourcePluginEnum.LOCAL)
    for ds in data_sources:
        ds.field_mapping = [m for m in ds.field_mapping if m["target_field"] != field_name]

    DataSource.objects.bulk_update(data_sources, fields=["field_mapping", "updated_at"])


@app.task(base=BaseTask, ignore_result=True)
def remove_dropped_field_in_user_extras(tenant_id: str, field_name: str):
    """删除租户某个用户自定义字段后，会将数据源用户 Extras 中的数据也一并清除"""
    users = DataSourceUser.objects.filter(
        data_source__owner_tenant_id=tenant_id,
        extras__has_key=field_name,
    )
    for u in users:
        u.extras.pop(field_name)

    DataSourceUser.objects.bulk_update(
        users, fields=["extras", "updated_at"], batch_size=USER_EXTRAS_UPDATE_BATCH_SIZE
    )


@app.task(base=BaseTask, ignore_result=True)
def migrate_user_extras_with_mapping(tenant_id: str, field_name: str, mapping: Dict):
    """
    更新租户用户自定义字段后，可能需要处理存量的数据

    如果是枚举类型，则需要根据迁移映射的配置，将数据进行转换
    如果只是普通类型（如数值，字符串），则不需要进行操作
    """
    # 前置的序列化器会确保数据合法，且只有枚举/多选枚举类型的 mapping 会有值
    if not mapping:
        return

    users = DataSourceUser.objects.filter(
        data_source__owner_tenant_id=tenant_id,
        extras__has_key=field_name,
    )
    for u in users:
        value = u.extras[field_name]
        if isinstance(value, list):
            # 先 set 后 list，避免出现映射后重复的情况
            u.extras[field_name] = list({mapping.get(v, v) for v in value})
        elif isinstance(value, str):
            u.extras[field_name] = mapping.get(value, value)

    DataSourceUser.objects.bulk_update(
        users, fields=["extras", "updated_at"], batch_size=USER_EXTRAS_UPDATE_BATCH_SIZE
    )
