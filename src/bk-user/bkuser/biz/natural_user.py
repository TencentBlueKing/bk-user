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
from typing import List, Optional

from pydantic import BaseModel

from bkuser.apps.natural_user.models import DataSourceUserNaturalUserRelation
from bkuser.apps.tenant.models import TenantUser
from bkuser.common.error_codes import error_codes


class TenantBaseInfo(BaseModel):
    id: str
    name: str


class TenantUserBaseInfo(BaseModel):
    id: str
    username: str
    full_name: str
    tenant: TenantBaseInfo


class NaturalUserInfo(BaseModel):
    id: str
    full_name: str
    data_source_user_ids: List[int]


class NaturalUserWithTenantUsers(BaseModel):
    id: str
    full_name: str
    tenant_users: List[TenantUserBaseInfo]


class NatureUserHandler:
    @staticmethod
    def get_nature_user_by_tenant_user_id(tenant_user_id: str) -> Optional[NaturalUserInfo]:
        """
        通过租户用户ID获取对应的自然人ID
        """
        tenant_user = TenantUser.objects.filter(id=tenant_user_id).first()
        if not tenant_user:
            raise error_codes.GET_CURRENT_TENANT_USER_ID_FAILED

        natural_user = DataSourceUserNaturalUserRelation.objects.filter(
            data_source_user_id=tenant_user.data_source_user_id
        ).first()
        if not natural_user:
            return None

        return NaturalUserInfo(
            id=natural_user.id,
            full_name=natural_user.name,
            data_source_user_ids=list(
                DataSourceUserNaturalUserRelation.objects.filter(nature_user=natural_user.id).values_list(
                    "data_source_user_id", flat=True
                )
            ),
        )