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
from typing import List

from pydantic import BaseModel

from bkuser.apps.natural_user.models import DataSourceUserNaturalUserRelation
from bkuser.apps.tenant.models import TenantUser
from bkuser.common.error_codes import error_codes


class NaturalUserInfo(BaseModel):
    id: str
    full_name: str
    data_source_user_ids: List[int]


class NatureUserHandler:
    @staticmethod
    def get_nature_user_by_tenant_user_id(tenant_user_id: str) -> NaturalUserInfo:
        """
        通过租户用户ID获取对应的自然人信息:
        存在两种情况:
        1. 未绑定自然人，则返回（伪）自然人=>租户用户的对应信息，及其对应的数据源用户id
        2. 绑定了自然人，返回自然人数据，及其绑定的数据用户id列表
        """
        tenant_user = TenantUser.objects.filter(id=tenant_user_id).first()
        if not tenant_user:
            raise error_codes.TENANT_USER_NOT_EXIST

        natural_user_relation = DataSourceUserNaturalUserRelation.objects.filter(
            data_source_user=tenant_user.data_source_user
        ).first()
        if not natural_user_relation:
            # 未绑定自然人，则返回（伪）自然人=>租户用户信息
            return NaturalUserInfo(
                id=tenant_user.id,
                full_name=tenant_user.data_source_user.full_name,
                data_source_user_ids=[tenant_user.data_source_user_id],
            )

        # 绑定自然人，则返回自然人信息
        natural_user = natural_user_relation.natural_user
        return NaturalUserInfo(
            id=natural_user.id,
            full_name=natural_user.full_name,
            data_source_user_ids=list(
                DataSourceUserNaturalUserRelation.objects.filter(natural_user=natural_user).values_list(
                    "data_source_user_id", flat=True
                )
            ),
        )
