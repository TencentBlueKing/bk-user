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
import logging
from collections import defaultdict
from typing import Dict, List, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from pydantic import BaseModel

from bkuser.apps.data_source.models import (
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.biz.data_source_organization import DataSourceDepartmentHandler

logger = logging.getLogger(__name__)


class TenantDepartmentInfo(BaseModel):
    id: int
    name: str


class TenantDepartmentInfoWithChildren(TenantDepartmentInfo):
    has_children: bool


class TenantUserLeaderInfo(BaseModel):
    id: str
    username: str
    full_name: str


class TenantUserPhoneInfo(BaseModel):
    is_inherited_phone: bool
    custom_phone: Optional[str] = ""
    custom_phone_country_code: Optional[str] = settings.DEFAULT_PHONE_COUNTRY_CODE


class TenantUserEmailInfo(BaseModel):
    is_inherited_email: bool
    custom_email: Optional[str] = ""


class TenantUserHandler:
    @staticmethod
    def get_tenant_user_leader_infos(tenant_user: TenantUser) -> List[TenantUserLeaderInfo]:
        """获取某个租户用户的 Leader 信息"""
        relations = DataSourceUserLeaderRelation.objects.filter(user_id=tenant_user.data_source_user_id)
        if not relations.exists():
            return []

        leaders = TenantUser.objects.filter(
            data_source_user_id__in=[rel.leader_id for rel in relations],
            tenant_id=tenant_user.tenant_id,
        ).select_related("data_source_user")

        return [
            TenantUserLeaderInfo(
                id=ld.id,
                username=ld.data_source_user.username,
                full_name=ld.data_source_user.full_name,
            )
            for ld in leaders
        ]

    @staticmethod
    def get_tenant_users_depts_map(
        tenant_id: str, tenant_users: List[TenantUser]
    ) -> Dict[str, List[TenantDepartmentInfo]]:
        """
        获取一批租户用户的部门信息

        :return: {租户用户 ID: [租户部门信息]}
        """
        # {数据源部门 ID: 租户部门信息(id, name)}
        data_source_dept_id_tenant_dept_info_map = {
            dept.data_source_department_id: TenantDepartmentInfo(id=dept.id, name=dept.data_source_department.name)
            for dept in TenantDepartment.objects.filter(tenant_id=tenant_id).select_related("data_source_department")
        }

        data_source_user_ids = [u.data_source_user_id for u in tenant_users]
        # {数据源用户 ID: [数据源部门 ID1, 数据源部门 ID2]}
        data_source_user_dept_ids_map = defaultdict(list)
        for rel in DataSourceDepartmentUserRelation.objects.filter(user_id__in=data_source_user_ids):
            data_source_user_dept_ids_map[rel.user_id].append(rel.department_id)

        return {
            user.id: [
                data_source_dept_id_tenant_dept_info_map[dept_id]
                for dept_id in data_source_user_dept_ids_map.get(user.data_source_user_id, [])
            ]
            for user in tenant_users
        }

    @staticmethod
    def update_tenant_user_phone(tenant_user: TenantUser, phone_info: TenantUserPhoneInfo):
        tenant_user.is_inherited_phone = phone_info.is_inherited_phone
        if not phone_info.is_inherited_phone:
            tenant_user.custom_phone = phone_info.custom_phone
            tenant_user.custom_phone_country_code = phone_info.custom_phone_country_code
        tenant_user.save()

    @staticmethod
    def update_tenant_user_email(tenant_user: TenantUser, email_info: TenantUserEmailInfo):
        tenant_user.is_inherited_email = email_info.is_inherited_email
        if not email_info.is_inherited_email:
            tenant_user.custom_email = email_info.custom_email
        tenant_user.save()

    @staticmethod
    def generate_tenant_user_display_name(user: TenantUser) -> str:
        # TODO (su) 支持读取表达式并渲染
        return f"{user.data_source_user.full_name}"

    @staticmethod
    def get_tenant_user_display_name_map_by_ids(tenant_user_ids: List[str]) -> Dict[str, str]:
        """
        根据指定的租户用户 ID 列表，获取对应的展示用名称列表

        :return: {user_id: user_display_name}
        """
        # 1. 尝试从 TenantUser 表根据表达式渲染出展示用名称
        display_name_map = {
            user.id: TenantUserHandler.generate_tenant_user_display_name(user)
            for user in TenantUser.objects.select_related("data_source_user").filter(id__in=tenant_user_ids)
        }
        # 2. 针对可能出现的 TenantUser 中被删除的 user_id，尝试从 User 表获取展示用名称（登录过就有记录）
        if not_exists_user_ids := set(tenant_user_ids) - set(display_name_map.keys()):
            logger.warning(
                "tenant user ids: %s not exists in TenantUser model, try find display name in User Model",
                not_exists_user_ids,
            )
            UserModel = get_user_model()  # noqa: N806
            for user in UserModel.objects.filter(username__in=not_exists_user_ids):
                # FIXME (nan) get_property 有 N+1 的风险，需要处理
                display_name_map[user.username] = user.get_property("display_name") or user.username

        # 3. 前两种方式都失效，那就给啥 user_id 就返回啥，避免调用的地方还需要处理
        if not_exists_user_ids := set(tenant_user_ids) - set(display_name_map.keys()):
            for user_id in not_exists_user_ids:
                display_name_map[user_id] = user_id

        return display_name_map


class TenantDepartmentHandler:
    @staticmethod
    def get_tenant_dept_children_infos(tenant_dept: TenantDepartment) -> List[TenantDepartmentInfoWithChildren]:
        """获取租户部门的子部门信息 TODO (su) DEPRECATED"""
        relation = DataSourceDepartmentRelation.objects.filter(
            department_id=tenant_dept.data_source_department_id,
        ).first()
        # 完全独立的部门（没有和其他部门进行关联）的情况
        if not relation:
            return []

        # 子部门数据源部门 ID
        sub_data_source_dept_ids = (
            DataSourceDepartmentRelation.objects.get(department_id=tenant_dept.data_source_department_id)
            .get_children()
            .values_list("department_id", flat=True)
        )
        sub_tenant_depts = TenantDepartment.objects.filter(
            tenant=tenant_dept.tenant,
            data_source_department_id__in=sub_data_source_dept_ids,
        ).select_related("data_source_department")
        # 子部门的子部门（孙子部门）信息
        sub_sub_dept_ids_map = DataSourceDepartmentHandler.get_sub_data_source_dept_ids_map(sub_data_source_dept_ids)

        return [
            TenantDepartmentInfoWithChildren(
                id=dept.id,
                name=dept.data_source_department.name,
                has_children=bool(len(sub_sub_dept_ids_map[dept.data_source_department_id])),
            )
            for dept in sub_tenant_depts
        ]
