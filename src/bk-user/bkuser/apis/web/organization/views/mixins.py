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
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from django.utils.translation import gettext_lazy as _

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.common.error_codes import error_codes


class CurrentUserTenantDataSourceMixin(CurrentUserTenantMixin):
    """获取当前用户所在租户指定条件数据源"""

    def get_current_tenant_real_data_source(self) -> DataSource:
        data_source = DataSource.objects.filter(
            owner_tenant_id=self.get_current_tenant_id(), type=DataSourceTypeEnum.REAL
        ).first()
        if not data_source:
            raise error_codes.DATA_SOURCE_NOT_EXIST.f(_("当前租户不存在实名用户数据源"))

        return data_source

    def get_current_tenant_local_real_data_source(self) -> DataSource:
        real_data_source = self.get_current_tenant_real_data_source()
        if not real_data_source.is_local:
            raise error_codes.DATA_SOURCE_NOT_EXIST.f(_("当前租户不存在本地实名用户数据源"))

        return real_data_source
