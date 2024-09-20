# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourcePlugin
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.plugins.local.models import LocalDataSourcePluginConfig


class CurrentTenantVirtualDataSource(CurrentUserTenantMixin):
    """当前租户虚拟数据源"""

    def get_current_virtual_data_source(self):
        data_source, _ = DataSource.objects.get_or_create(
            owner_tenant_id=self.get_current_tenant_id(),
            type=DataSourceTypeEnum.VIRTUAL,
            defaults={
                "plugin": DataSourcePlugin.objects.get(id=DataSourcePluginEnum.LOCAL),
                "plugin_config": LocalDataSourcePluginConfig(enable_password=False),
            },
        )

        return data_source
