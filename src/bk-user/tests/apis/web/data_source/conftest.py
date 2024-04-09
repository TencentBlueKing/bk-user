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
import datetime
from typing import Any, Dict, List

import pytest
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.sync.constants import SyncTaskStatus, SyncTaskTrigger
from bkuser.apps.sync.models import DataSourceSyncTask
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

pytestmark = pytest.mark.django_db


@pytest.fixture()
def data_source(random_tenant, local_ds_plugin_cfg) -> DataSource:
    # FIXME (su) 使用 data_source 这个 fixture 其实可以不用 random_tenant，因为使用了 get_or_create
    # 在移除默认租户的初始化 migration 中创建的 real 类型的数据源后，可以批量删除 random_tenant 逻辑
    ds, _ = DataSource.objects.get_or_create(
        owner_tenant_id=random_tenant.id,
        type=DataSourceTypeEnum.REAL,
        plugin_id=DataSourcePluginEnum.LOCAL,
        defaults={"plugin_config": LocalDataSourcePluginConfig(**local_ds_plugin_cfg)},
    )
    return ds


@pytest.fixture()
def field_mapping(request) -> List[Dict]:
    """字段映射，不含自定义字段"""
    fields = ["username", "full_name", "phone_country_code", "phone", "email"]
    if "tenant_user_custom_fields" in request.fixturenames:
        fields += [f.name for f in request.getfixturevalue("tenant_user_custom_fields")]

    return [{"source_field": f, "mapping_operation": "direct", "target_field": f} for f in fields]


@pytest.fixture()
def sync_config() -> Dict[str, Any]:
    """数据源同步配置"""
    return {"sync_period": 30}


@pytest.fixture()
def data_source_sync_tasks(data_source) -> List[DataSourceSyncTask]:
    success_task = DataSourceSyncTask.objects.create(
        data_source=data_source,
        status=SyncTaskStatus.SUCCESS,
        has_warning=True,
        trigger=SyncTaskTrigger.CRONTAB,
        duration=datetime.timedelta(seconds=5),
        logs="sync task success!",
        extras={"async_run": True, "overwrite": True},
    )
    failed_task = DataSourceSyncTask.objects.create(
        data_source=data_source,
        status=SyncTaskStatus.FAILED,
        has_warning=False,
        trigger=SyncTaskTrigger.MANUAL,
        duration=datetime.timedelta(minutes=5),
        logs="sync task failed!",
        extras={"async_run": True, "overwrite": True},
    )
    other_tenant_task = DataSourceSyncTask.objects.create(
        data_source_id=999,
        status=SyncTaskStatus.SUCCESS,
        has_warning=False,
        trigger=SyncTaskTrigger.SIGNAL,
        duration=datetime.timedelta(seconds=15),
        logs="sync task success!",
        extras={"async_run": True, "overwrite": True},
    )
    return [success_task, failed_task, other_tenant_task]
