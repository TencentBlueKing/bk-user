# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
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
from collections import defaultdict
from typing import Dict, List

from django.utils.translation import gettext_lazy as _

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource, DataSourceDepartmentUserRelation, DataSourceUserLeaderRelation
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


class CurrentUserDepartmentRelationMixin:
    """获取用户与部门之间的映射关系"""

    def get_user_department_map(self, data_source_user_ids: List[int]) -> Dict:
        # 记录用户与部门之间的映射关系
        user_department_relations = DataSourceDepartmentUserRelation.objects.filter(
            user_id__in=data_source_user_ids
        ).values("department_id", "user_id")
        user_department_map = defaultdict(list)

        # 将用户的所有部门存储在列表中
        for relation in user_department_relations:
            user_department_map[relation["user_id"]].append(relation["department_id"])

        return user_department_map


class CurrentUserLeaderRelationMixin:
    """获取用户与上级之间的映射关系"""

    def get_user_leader_map(self, data_source_user_ids: List[int]) -> Dict:
        # 记录用户与上级之间的映射关系
        user_leader_relations = DataSourceUserLeaderRelation.objects.filter(user_id__in=data_source_user_ids).values(
            "leader_id", "user_id"
        )
        user_leader_map = defaultdict(list)

        # 将用户的所有上级存储在列表中
        for relation in user_leader_relations:
            user_leader_map[relation["user_id"]].append(relation["leader_id"])

        return user_leader_map
