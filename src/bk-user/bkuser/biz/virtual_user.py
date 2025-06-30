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
from datetime import datetime
from typing import List, Union

from pydantic import BaseModel

from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.tenant.models import TenantUser, VirtualUserAppRelation, VirtualUserOwnerRelation
from bkuser.apps.tenant.utils import TenantUserIDGenerator


class DetailedVirtualUser(BaseModel):
    """详细虚拟用户信息"""

    id: str
    username: str
    full_name: str
    owners: List[str]
    app_codes: List[str]
    created_at: datetime


def to_detailed_virtual_users(
    tenant_users: Union[TenantUser, List[TenantUser]],
) -> Union[DetailedVirtualUser, List[DetailedVirtualUser]]:
    """将 TenantUser 对象转换为 DetailedVirtualUser 模型

    :param tenant_users: 单个 TenantUser 或 TenantUser 列表
    :return: 单个 DetailedVirtualUser 或 DetailedVirtualUser 列表
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

    # 转换为 DetailedVirtualUser 列表
    return [
        DetailedVirtualUser(
            id=tenant_user.id,
            username=tenant_user.data_source_user.username,
            full_name=tenant_user.data_source_user.full_name,
            app_codes=app_codes_map[tenant_user.id],
            owners=owners_map[tenant_user.id],
            created_at=tenant_user.created_at,
        )
        for tenant_user in tenant_users
    ]


def _to_single_detailed_virtual_user(tenant_user: TenantUser) -> DetailedVirtualUser:
    """转换单个 TenantUser 为 DetailedVirtualUser"""
    # 查询 app_codes
    app_codes = list(VirtualUserAppRelation.objects.filter(tenant_user=tenant_user).values_list("app_code", flat=True))

    # 查询 owners
    owners = list(VirtualUserOwnerRelation.objects.filter(tenant_user=tenant_user).values_list("owner_id", flat=True))

    return DetailedVirtualUser(
        id=tenant_user.id,
        username=tenant_user.data_source_user.username,
        full_name=tenant_user.data_source_user.full_name,
        app_codes=app_codes,
        owners=owners,
        created_at=tenant_user.created_at,
    )


class VirtualUserHandler:
    @staticmethod
    def create(data_source: DataSource, username: str, full_name: str) -> TenantUser:
        """创建虚拟用户需要的数据源用户 & 租户用户

        :param data_source: 数据源对象
        :param username: 用户名
        :param full_name: 用户姓名
        """
        ds_user = DataSourceUser.objects.create(
            data_source=data_source,
            code=username,
            username=username,
            full_name=full_name,
        )

        tenant_id = data_source.owner_tenant_id

        return TenantUser.objects.create(
            id=TenantUserIDGenerator(tenant_id, data_source).gen(ds_user),
            tenant_id=tenant_id,
            data_source_user=ds_user,
            data_source=data_source,
        )

    @staticmethod
    def set_app_codes(tenant_user: TenantUser, app_codes: List[str]) -> None:
        """设置虚拟用户和 app_code 之间的关联"""
        VirtualUserAppRelation.objects.bulk_create(
            [VirtualUserAppRelation(tenant_user=tenant_user, app_code=app_code) for app_code in app_codes]
        )

    @staticmethod
    def set_owners(tenant_user: TenantUser, owners: List[str]) -> None:
        """设置虚拟用户和责任人之间的关联"""
        VirtualUserOwnerRelation.objects.bulk_create(
            [VirtualUserOwnerRelation(tenant_user=tenant_user, owner_id=owner) for owner in owners]
        )

    @staticmethod
    def update_app_codes(tenant_user: TenantUser, new_app_codes: List[str]) -> None:
        """更新虚拟用户与 app_code 关联 (增量更新，仅修改差异部分)"""
        cur_app_codes_set = set(
            VirtualUserAppRelation.objects.filter(tenant_user=tenant_user).values_list("app_code", flat=True)
        )
        new_app_codes_set = set(new_app_codes)

        if should_delete := cur_app_codes_set - new_app_codes_set:
            VirtualUserAppRelation.objects.filter(tenant_user=tenant_user, app_code__in=should_delete).delete()

        if should_create := new_app_codes_set - cur_app_codes_set:
            VirtualUserHandler.set_app_codes(tenant_user, list(should_create))

    @staticmethod
    def update_owners(tenant_user: TenantUser, new_owners: List[str]) -> None:
        """更新虚拟用户与责任人之间的关联 (增量更新，仅修改差异部分)"""
        cur_owners_set = set(
            VirtualUserOwnerRelation.objects.filter(tenant_user=tenant_user).values_list("owner_id", flat=True)
        )
        new_owners_set = set(new_owners)

        if should_delete := cur_owners_set - new_owners_set:
            VirtualUserOwnerRelation.objects.filter(tenant_user=tenant_user, owner_id__in=should_delete).delete()

        if should_create := new_owners_set - cur_owners_set:
            VirtualUserHandler.set_owners(tenant_user, list(should_create))
