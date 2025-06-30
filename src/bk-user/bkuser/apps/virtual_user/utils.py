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
from typing import List, Union

from bkuser.apps.tenant.models import TenantUser, VirtualUserAppRelation, VirtualUserOwnerRelation
from bkuser.apps.virtual_user.data_models import ToDetailedVirtualUser


def to_detailed_virtual_users(
    tenant_users: Union[TenantUser, List[TenantUser]],
) -> Union[ToDetailedVirtualUser, List[ToDetailedVirtualUser]]:
    """将 TenantUser 对象转换为 ToDetailedVirtualUser 模型

    :param tenant_users: 单个 TenantUser 或 TenantUser 列表
    :return: 单个 ToDetailedVirtualUser 或 ToDetailedVirtualUser 列表
    """
    if isinstance(tenant_users, TenantUser):
        return _to_single_detailed_virtual_user(tenant_users)

    if not tenant_users:
        return []

    # 批量查询关联数据
    tenant_user_ids = [user.id for user in tenant_users]

    # 查询 app_codes
    app_relations = VirtualUserAppRelation.objects.filter(tenant_user_id__in=tenant_user_ids).values_list(
        "tenant_user_id", "app_code"
    )
    app_codes_map = defaultdict(list)
    for tenant_user_id, app_code in app_relations:
        app_codes_map[tenant_user_id].append(app_code)

    # 查询 owners
    owner_relations = VirtualUserOwnerRelation.objects.filter(tenant_user_id__in=tenant_user_ids).values_list(
        "tenant_user_id", "owner_id"
    )
    owners_map = defaultdict(list)
    for tenant_user_id, owner_id in owner_relations:
        owners_map[tenant_user_id].append(owner_id)

    # 转换为 ToDetailedVirtualUser 列表
    return [
        ToDetailedVirtualUser(
            id=tenant_user.id,
            username=tenant_user.data_source_user.username,
            full_name=tenant_user.data_source_user.full_name,
            app_codes=app_codes_map[tenant_user.id],
            owners=owners_map[tenant_user.id],
            created_at=tenant_user.created_at,
        )
        for tenant_user in tenant_users
    ]


def _to_single_detailed_virtual_user(tenant_user: TenantUser) -> ToDetailedVirtualUser:
    """转换单个 TenantUser 为 ToDetailedVirtualUser"""
    # 查询 app_codes
    app_codes = list(VirtualUserAppRelation.objects.filter(tenant_user=tenant_user).values_list("app_code", flat=True))

    # 查询 owners
    owners = list(VirtualUserOwnerRelation.objects.filter(tenant_user=tenant_user).values_list("owner_id", flat=True))

    return ToDetailedVirtualUser(
        id=tenant_user.id,
        username=tenant_user.data_source_user.username,
        full_name=tenant_user.data_source_user.full_name,
        app_codes=app_codes,
        owners=owners,
        created_at=tenant_user.created_at,
    )
