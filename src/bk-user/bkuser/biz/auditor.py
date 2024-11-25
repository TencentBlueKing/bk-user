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

from bkuser.apps.audit.constants import ObjectTypeEnum, OperationEnum
from bkuser.apps.audit.data_models import AuditObject
from bkuser.apps.audit.recorder import batch_add_audit_records
from bkuser.apps.data_source.models import (
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.tenant.models import TenantUser
from bkuser.utils.django import get_model_dict


class TenantUserUpdateDestroyAuditor:
    """用于记录租户用户修改与删除的审计"""

    def __init__(self, operator: str, tenant_id: str, is_delete: bool = False):
        self.operator = operator
        self.tenant_id = tenant_id
        self.is_delete = is_delete

        self.data_befores: Dict[str, Dict] = {}
        self.audit_objects: List[AuditObject] = []

    def pre_record_data_before(self, tenant_user: TenantUser, data_source_user: DataSourceUser):
        """记录变更前的相关数据记录"""

        # 为每个用户的审计数据创建唯一的键
        tenant_user_id = tenant_user.id

        # 初始化对应 tenant_user 的审计数据
        self.data_befores[tenant_user_id] = {
            "tenant_user": get_model_dict(tenant_user),
            "data_source_user": get_model_dict(data_source_user),
            "collaboration_tenant_users": {},
            # 记录修改前的用户部门
            "department_ids": list(
                DataSourceDepartmentUserRelation.objects.filter(
                    user=data_source_user,
                ).values_list("department_id", flat=True)
            ),
            # 记录修改前的用户上级
            "leader_ids": list(
                DataSourceUserLeaderRelation.objects.filter(user=data_source_user).values_list("leader_id", flat=True)
            ),
        }

        # 记录修改前的协同租户用户
        if self.is_delete:
            # 获取与 data_source_user_id 相关的所有 collab_user，排除当前的 tenant_user
            collab_users = TenantUser.objects.filter(data_source_user_id=data_source_user.id).exclude(
                id=tenant_user.id
            )

            # 构造每一个租户用户的 collab_user 映射
            self.data_befores[tenant_user_id]["collaboration_tenant_users"] = {
                collab_user.id: get_model_dict(collab_user) for collab_user in collab_users
            }

    def batch_pre_record_data_before(self, tenant_users: List[TenantUser]):
        """批量记录变更前的相关数据记录"""

        for tenant_user in tenant_users:
            self.pre_record_data_before(tenant_user, tenant_user.data_source_user)

    def get_current_operation(self, operation: OperationEnum) -> OperationEnum:
        """根据操作行为返回对应的修改或删除操作"""

        operation_map = {
            OperationEnum.MODIFY_DATA_SOURCE_USER: OperationEnum.DELETE_DATA_SOURCE_USER,
            OperationEnum.MODIFY_USER_DEPARTMENT: OperationEnum.DELETE_USER_DEPARTMENT,
            OperationEnum.MODIFY_USER_LEADER: OperationEnum.DELETE_USER_LEADER,
            OperationEnum.MODIFY_TENANT_USER: OperationEnum.DELETE_TENANT_USER,
        }

        return operation_map[operation] if self.is_delete else operation

    def record(self, tenant_user: TenantUser, data_source_user: DataSourceUser):
        """组装相关数据，并调用 apps.audit 模块里的方法进行记录"""
        tenant_user_id = tenant_user.id

        ds_user_id = (
            self.data_befores[tenant_user_id]["data_source_user"]["id"] if self.is_delete else data_source_user.id
        )
        ds_user_name = (
            self.data_befores[tenant_user_id]["data_source_user"]["username"]
            if self.is_delete
            else data_source_user.username
        )

        ds_user_object = {"id": ds_user_id, "name": ds_user_name, "type": ObjectTypeEnum.DATA_SOURCE_USER}

        self.audit_objects.extend(
            [
                # 数据源用户本身信息
                AuditObject(
                    **ds_user_object,
                    operation=self.get_current_operation(OperationEnum.MODIFY_DATA_SOURCE_USER),
                    data_before=self.data_befores[tenant_user_id]["data_source_user"],
                    data_after=get_model_dict(data_source_user) if not self.is_delete else {},
                ),
                # 数据源用户的部门
                AuditObject(
                    **ds_user_object,
                    operation=self.get_current_operation(OperationEnum.MODIFY_USER_DEPARTMENT),
                    data_before={"department_ids": self.data_befores[tenant_user_id]["department_ids"]},
                    data_after={
                        "department_ids": list(
                            DataSourceDepartmentUserRelation.objects.filter(
                                user=data_source_user,
                            ).values_list("department_id", flat=True)
                        )
                        if not self.is_delete
                        else []
                    },
                ),
                # 数据源用户的 Leader
                AuditObject(
                    **ds_user_object,
                    operation=self.get_current_operation(OperationEnum.MODIFY_USER_LEADER),
                    data_before={"leader_ids": self.data_befores[tenant_user_id]["leader_ids"]},
                    data_after={
                        "leader_ids": list(
                            DataSourceUserLeaderRelation.objects.filter(user=data_source_user).values_list(
                                "leader_id", flat=True
                            )
                        )
                        if not self.is_delete
                        else []
                    },
                ),
                # 租户用户
                AuditObject(
                    id=tenant_user.id,
                    type=ObjectTypeEnum.TENANT_USER,
                    operation=self.get_current_operation(OperationEnum.MODIFY_TENANT_USER),
                    data_before=self.data_befores[tenant_user_id]["tenant_user"],
                    data_after=get_model_dict(tenant_user) if not self.is_delete else {},
                ),
            ]
        )

        # 若为删除操作，则需记录删除前的协同租户用户
        if self.is_delete:
            self.audit_objects.extend(
                [
                    AuditObject(
                        id=user_id,
                        type=ObjectTypeEnum.TENANT_USER,
                        operation=OperationEnum.DELETE_COLLABORATION_TENANT_USER,
                        data_before=user_data,
                        data_after={},
                    )
                    for user_id, user_data in self.data_befores[tenant_user_id]["collaboration_tenant_users"].items()
                ]
            )

    def batch_record(self, tenant_users: List[TenantUser]):
        """批量记录"""

        for tenant_user in tenant_users:
            self.record(tenant_user, tenant_user.data_source_user)

    # 由于不确定操作是否为批量，故将底层存储数据库的方法抽象，需单独调用
    def save_audit_records(self):
        batch_add_audit_records(self.operator, self.tenant_id, self.audit_objects)


class TenantUserCreateAuditor:
    """用于记录租户用户创建的审计"""

    def __init__(self, operator: str, tenant_id: str):
        self.operator = operator
        self.tenant_id = tenant_id
        self.audit_objects: List[AuditObject] = []

    def record(self, tenant_user: TenantUser, data_source_user: DataSourceUser):
        """组装相关数据，并调用 apps.audit 模块里的方法进行记录"""
        ds_user_object = {
            "id": data_source_user.id,
            "name": data_source_user.username,
            "type": ObjectTypeEnum.DATA_SOURCE_USER,
        }

        self.audit_objects.extend(
            [
                # 数据源用户本身信息
                AuditObject(
                    **ds_user_object,
                    operation=OperationEnum.CREATE_DATA_SOURCE_USER,
                    data_before={},
                    data_after=get_model_dict(data_source_user),
                ),
                # 数据源用户的部门
                AuditObject(
                    **ds_user_object,
                    operation=OperationEnum.CREATE_USER_DEPARTMENT,
                    data_before={},
                    data_after={
                        "department_ids": list(
                            DataSourceDepartmentUserRelation.objects.filter(
                                user=data_source_user,
                            ).values_list("department_id", flat=True)
                        )
                    },
                ),
                # 租户用户（包含协同租户用户）
                AuditObject(
                    id=tenant_user.id,
                    type=ObjectTypeEnum.TENANT_USER,
                    operation=OperationEnum.CREATE_COLLABORATION_TENANT_USER
                    if tenant_user.tenant_id != self.tenant_id
                    else OperationEnum.CREATE_TENANT_USER,
                    data_before={},
                    data_after=get_model_dict(tenant_user),
                ),
            ]
        )

    def batch_record(self, tenant_users: List[TenantUser]):
        """批量记录"""

        for tenant_user in tenant_users:
            self.record(tenant_user, tenant_user.data_source_user)
        batch_add_audit_records(self.operator, self.tenant_id, self.audit_objects)


class TenantUserDepartmentRelationsAuditor:
    """用于记录用户-部门关系变更的审计"""

    def __init__(self, operator: str, tenant_id: str, data_source_user_ids: List[int]):
        self.operator = operator
        self.tenant_id = tenant_id
        self.audit_objects: List[AuditObject] = []
        self.data_before: Dict[int, Dict] = {}
        self.data_source_user_ids = data_source_user_ids

    def pre_record_data_before(self):
        """记录变更前的相关数据记录"""
        # 获取用户与部门之间的映射关系
        data_before_map = self.get_user_department_map(self.data_source_user_ids)

        # 初始化 data_before, 记录变更前用户与部门之间的映射关系
        for data_source_user_id in self.data_source_user_ids:
            self.data_before[data_source_user_id] = {"department_ids": data_before_map.get(data_source_user_id, [])}

    def record(self, data_source_user: DataSourceUser, data_before: Dict, data_after: Dict, extras: Dict):
        """调用 apps.audit 模块里的方法进行记录"""
        self.audit_objects.append(
            AuditObject(
                id=data_source_user.id,
                name=data_source_user.username,
                type=ObjectTypeEnum.DATA_SOURCE_USER,
                operation=OperationEnum.MODIFY_USER_DEPARTMENT,
                data_before=data_before,
                data_after=data_after,
                extras=extras,
            )
        )

    def batch_record(self, extras: Dict[str, List]):
        """批量记录"""
        data_source_users = DataSourceUser.objects.filter(
            id__in=self.data_source_user_ids,
        )
        # 记录变更后的用户与部门之间的映射关系
        data_after_map = self.get_user_department_map(self.data_source_user_ids)

        for data_source_user in data_source_users:
            data_before = self.data_before[data_source_user.id]
            data_after = {"department_ids": data_after_map.get(data_source_user.id, [])}
            self.record(data_source_user, data_before, data_after, extras)
        batch_add_audit_records(self.operator, self.tenant_id, self.audit_objects)

    @staticmethod
    def get_user_department_map(data_source_user_ids: List[int]) -> Dict:
        """记录用户与部门之间的映射关系"""
        user_department_relations = DataSourceDepartmentUserRelation.objects.filter(
            user_id__in=data_source_user_ids
        ).values("department_id", "user_id")
        user_department_map = defaultdict(list)

        # 将用户的所有部门存储在列表中
        for relation in user_department_relations:
            user_department_map[relation["user_id"]].append(relation["department_id"])

        return user_department_map
