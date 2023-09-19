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
from django.dispatch import receiver

from bkuser.apps.data_source.initializers import LocalDataSourceIdentityInfoInitializer
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.sync.data_models import TenantSyncOptions
from bkuser.apps.sync.managers import TenantSyncManager
from bkuser.apps.sync.signals import post_sync_data_source


@receiver(post_sync_data_source)
def initialize_local_data_source_identity_info(sender, data_source: DataSource, **kwargs):
    """在完成数据源同步后，需要对本地数据源的用户账密信息做初始化"""
    LocalDataSourceIdentityInfoInitializer(data_source).initialize()


@receiver(post_sync_data_source)
def sync_tenant_departments_users(sender, data_source: DataSource, **kwargs):
    """同步租户数据（部门 & 用户）"""
    # TODO 目前没有跨租户协同，因此只要往数据源所属租户同步即可
    TenantSyncManager(data_source, data_source.owner_tenant_id, TenantSyncOptions()).execute()
