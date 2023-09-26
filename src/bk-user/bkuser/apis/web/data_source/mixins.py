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
from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.data_source.models import DataSource


class CurrentUserTenantDataSourceMixin(CurrentUserTenantMixin):
    """获取当前用户所在租户下属数据源"""

    lookup_url_kwarg = "id"

    def get_queryset(self):
        return DataSource.objects.filter(owner_tenant_id=self.get_current_tenant_id())
