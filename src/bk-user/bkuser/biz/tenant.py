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
from collections import defaultdict
from typing import Dict, List, Optional

from django.db import transaction
from pydantic import BaseModel

from bkuser.apps.data_source.models import DataSource, DataSourcePlugin
from bkuser.apps.data_source_organization.models import DataSourceUser
from bkuser.apps.tenant.models import Tenant, TenantManager
from bkuser.apps.tenant_organization.models import TenantUser
from bkuser.utils.uuid import generate_uuid


class DataSourceUserInfo(BaseModel):
    """数据源用户信息"""

    username: str
    full_name: str
    email: str
    phone: str
    phone_country_code: str


class TenantUserWithInheritedInfo(BaseModel):
    """租户用户，带其继承的用户信息"""

    id: str
    data_source_user: DataSourceUserInfo


class TenantFeatureFlag(BaseModel):
    """租户特性集"""

    user_number_visible: bool = False


class TenantBaseInfo(BaseModel):
    """租户基本信息"""

    id: str
    name: str
    logo: str = ""
    feature_flags: TenantFeatureFlag


class TenantEditableBaseInfo(BaseModel):
    """租户可编辑的基本信息"""

    name: str
    logo: str = ""
    feature_flags: TenantFeatureFlag


class TenantManagerWithoutID(BaseModel):
    username: str
    full_name: str
    email: str
    phone: str
    phone_country_code: str


class TenantUserHandler:
    @staticmethod
    def list_tenant_user_by_id(tenant_user_ids: List[str]) -> List[TenantUserWithInheritedInfo]:
        """
        查询租户用户信息
        """
        tenant_users = TenantUser.objects.filter(id__in=tenant_user_ids)
        data_source_user_ids = [i.data_source_user_id for i in tenant_users]

        # 查询关联的data_source_user
        data_source_users = DataSourceUser.objects.filter(id__in=data_source_user_ids)
        data_source_users_map = {i.id: i for i in data_source_users}

        # 返回租户用户本身信息和对应数据源用户信息
        data = []
        for i in tenant_users:
            data_source_user = data_source_users_map.get(i.data_source_user_id)
            # 对于数据源用户不存在，则表示该租户用户已经不可用
            if data_source_user is None:
                continue

            data.append(
                TenantUserWithInheritedInfo(
                    id=i.id,
                    data_source_user=DataSourceUser(
                        username=data_source_user.username,
                        full_name=data_source_user.full_name,
                        email=data_source_user.email,
                        phone=data_source_user.phone,
                        phone_country_code=data_source_user.phone_country_code,
                    ),
                )
            )

        return data


class TenantHandler:
    @staticmethod
    def get_tenant_manager_map(tenant_ids: Optional[List[str]] = None) -> Dict[str, List[TenantUserWithInheritedInfo]]:
        """
        查询租户管理员
        """
        tenant_managers = TenantManager.objects.all()
        if tenant_ids is not None:
            tenant_managers = tenant_managers.filter(tenant_id__in=tenant_ids)

        # 查询管理员对应的信息
        tenant_user_ids = [i.tenant_user_id for i in tenant_managers]
        tenant_users = TenantUserHandler.list_tenant_user_by_id(tenant_user_ids)
        tenant_users_map = {i.id: i for i in tenant_users}

        # 按照{tenant_id: List[tenant_user]}格式组装s
        data = defaultdict(list)
        for i in tenant_managers:
            tenant_user = tenant_users_map.get(i.tenant_user_id)
            if tenant_user is not None:
                data[i.tenant_id].append(tenant_user)

        return data

    @staticmethod
    def create_with_managers(tenant_info: TenantBaseInfo, managers: List[TenantManagerWithoutID]) -> str:
        """
        创建租户，支持同时创建租户管理员
        """
        with transaction.atomic():
            # 创建租户本身
            tenant = Tenant.objects.create(**tenant_info.model_dump())

            # TODO: 开发本地数据源时，重写（直接调用本地数据源Handler）
            # 创建本地数据源，名称则使用租户名称
            data_source = DataSource.objects.create(
                name=f"{tenant_info.name}-本地数据源",
                owner_tenant_id=tenant.id,
                plugin=DataSourcePlugin.objects.get(id="local"),
            )

            # 添加数据源用户和租户用户
            # Note: 批量创建无法返回ID，这里使用循环创建
            tenant_manager_objs = []
            for i in managers:
                # 创建数据源用户
                data_source_user = DataSourceUser.objects.create(data_source_id=data_source.id, **i.model_dump())
                # 创建对应的租户用户
                tenant_user = TenantUser.objects.create(
                    data_source_user_id=data_source_user.id,
                    tenant_id=tenant.id,
                    id=generate_uuid(),
                )

                tenant_manager_objs.append(TenantManager(tenant=tenant, tenant_user_id=tenant_user.id))

            if tenant_manager_objs:
                TenantManager.objects.bulk_create(tenant_manager_objs, batch_size=100)

        return tenant_info.id

    @staticmethod
    def update_with_managers(tenant_id: str, tenant_info: TenantEditableBaseInfo, manager_ids: List[str]):
        """
        【覆盖】更新租户
        """
        old_manager_ids = TenantManager.objects.filter(tenant_id=tenant_id).values_list("tenant_user_id", flat=True)

        # 新旧对比 => 需要删除的管理员ID，需要新增的管理员ID
        should_deleted_manager_ids = set(old_manager_ids) - set(manager_ids)
        should_add_manager_ids = set(manager_ids) - set(old_manager_ids)

        with transaction.atomic():
            # 更新基本信息
            Tenant.objects.filter(id=tenant_id).update(**tenant_info.model_dump())

            if should_deleted_manager_ids:
                TenantManager.objects.filter(
                    tenant_id=tenant_id, tenant_user_id__in=should_deleted_manager_ids
                ).delete()

            if should_add_manager_ids:
                TenantManager.objects.bulk_create(
                    [TenantManager(tenant_id=tenant_id, tenant_user_id=i) for i in should_add_manager_ids],
                    batch_size=100,
                )
