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

from bkuser.apps.data_source.models import DataSource, DataSourceDepartmentRelation, DataSourcePlugin, DataSourceUser
from bkuser.apps.tenant.models import Tenant, TenantDepartment, TenantManager, TenantUser
from bkuser.biz.data_source import DataSourceDepartmentHandler, DataSourceHandler, DataSourceSimpleInfo
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


class TenantDepartmentBaseInfo(BaseModel):
    id: int
    name: str
    has_children: bool


class TenantUserHandler:
    @staticmethod
    def list_tenant_user_by_id(tenant_user_ids: List[str]) -> List[TenantUserWithInheritedInfo]:
        """
        查询租户用户信息
        """
        tenant_users = TenantUser.objects.select_related("data_source_user").filter(id__in=tenant_user_ids)

        # 返回租户用户本身信息和对应数据源用户信息
        data = []
        for i in tenant_users:
            data_source_user = i.data_source_user
            # 对于数据源用户不存在，则表示该租户用户已经不可用
            if data_source_user is None:
                continue

            data.append(
                TenantUserWithInheritedInfo(
                    id=i.id,
                    data_source_user=DataSourceUserInfo(
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

        # 按照 {tenant_id: List[tenant_user]} 格式组装
        data = defaultdict(list)
        for i in tenant_managers:
            tenant_user = tenant_users_map.get(i.tenant_user_id)
            if tenant_user is not None:
                data[i.tenant_id].append(tenant_user)

        return data

    @staticmethod
    def retrieve_tenant_managers(tenant_id: str) -> List[TenantUserWithInheritedInfo]:
        """
        查询单个租户的租户管理员
        """
        # 查询单个租户的管理员对应的信息
        return TenantHandler.get_tenant_manager_map([tenant_id]).get(tenant_id) or []

    @staticmethod
    def create_with_managers(tenant_info: TenantBaseInfo, managers: List[TenantManagerWithoutID]) -> str:
        """
        创建租户，支持同时创建租户管理员
        """
        with transaction.atomic():
            # 创建租户本身
            tenant = Tenant.objects.create(**tenant_info.model_dump())

            # FIXME: 开发本地数据源时，重写（直接调用本地数据源Handler）
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
                data_source_user = DataSourceUser.objects.create(data_source=data_source, **i.model_dump())
                # 创建对应的租户用户
                tenant_user = TenantUser.objects.create(
                    data_source_user=data_source_user,
                    tenant=tenant,
                    data_source=data_source,
                    id=generate_uuid(),
                )

                tenant_manager_objs.append(TenantManager(tenant=tenant, tenant_user=tenant_user))

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

    @staticmethod
    def get_data_source_ids_map_by_id(tenant_ids: List[str]) -> Dict[str, List[int]]:
        # 当前属于租户的数据源
        tenant_data_source_map: Dict = {}
        data_sources: Dict[str, List[DataSourceSimpleInfo]] = DataSourceHandler.get_data_source_map_by_owner(
            tenant_ids
        )
        for tenant_id, data_source_list in data_sources.items():
            data_source_ids: List = [data_source.id for data_source in data_source_list]
            tenant_data_source_map[tenant_id] = data_source_ids
        # TODO 协同数据源获取
        return tenant_data_source_map


class TenantDepartmentHandler:
    @staticmethod
    def convert_data_source_department_to_tenant_department(
        tenant_id: str, data_source_department_ids: List[int]
    ) -> List[TenantDepartmentBaseInfo]:
        """
        转换为租户部门
        """
        # tenant_id 租户下部门关系映射
        tenant_departments = TenantDepartment.objects.filter(tenant_id=tenant_id)

        # 获取数据源部门基础信息
        data_source_departments = DataSourceDepartmentHandler.get_department_info_map_by_id(data_source_department_ids)

        # data_source_departments中包含了父子部门的ID，协同数据源需要查询绑定了该租户
        department_ids = list(data_source_departments.keys())
        for department in data_source_departments.values():
            department_ids += department.children_ids

        # NOTE: 协同数据源，可能存在未授权全部子部门
        # 提前拉取所有映射, 过滤绑定的租户部门
        tenant_departments = tenant_departments.filter(data_source_department_id__in=department_ids)
        if not tenant_departments.exists():
            return []

        # 已绑定该租户的数据源部门id
        bound_departments_ids = tenant_departments.values_list("data_source_department_id", flat=True)

        # 构建返回数据
        data: List[TenantDepartmentBaseInfo] = []
        for tenant_department in tenant_departments:
            # tenant_departments 包含了父子部门的租户映射关系,但是子部门非本次查询的入参，跳过
            data_source_department_id = tenant_department.data_source_department_id
            if data_source_department_id not in data_source_department_ids:
                continue
            # 部门基础信息
            data_source_department_info = data_source_departments[data_source_department_id]
            # 只要一个子部门被授权，都是存在子部门
            children_flag = [
                True for child in data_source_department_info.children_ids if child in bound_departments_ids
            ]
            data.append(
                TenantDepartmentBaseInfo(
                    id=tenant_department.id,
                    name=data_source_department_info.name,
                    has_children=any(children_flag),
                )
            )
        return data

    @staticmethod
    def get_tenant_root_department_map_by_tenant_id(
        tenant_ids: List[str], current_tenant_id: str
    ) -> Dict[str, List[TenantDepartmentBaseInfo]]:
        data_source_map = TenantHandler.get_data_source_ids_map_by_id(tenant_ids)

        # 通过获取数据源的根节点
        tenant_root_department_map: Dict = {}
        for tenant_id, data_source_ids in data_source_map.items():
            root_department_ids = (
                DataSourceDepartmentRelation.objects.root_nodes()
                .filter(data_source_id__in=data_source_ids)
                .values_list("department_id", flat=True)
            )
            # 转换数据源部门为当前为 current_tenant_id 租户的租户部门
            tenant_root_department = TenantDepartmentHandler.convert_data_source_department_to_tenant_department(
                tenant_id=current_tenant_id, data_source_department_ids=list(root_department_ids)
            )
            tenant_root_department_map[tenant_id] = tenant_root_department
        return tenant_root_department_map

    @staticmethod
    def get_tenant_department_children_by_id(tenant_department_id: int) -> List[TenantDepartmentBaseInfo]:
        tenant_department = TenantDepartment.objects.get(id=tenant_department_id)
        # 获取二级组织
        children = DataSourceDepartmentRelation.objects.get(
            department=tenant_department.data_source_department
        ).get_children()
        return TenantDepartmentHandler.convert_data_source_department_to_tenant_department(
            tenant_department.tenant_id, children.values_list("department_id", flat=True)
        )
