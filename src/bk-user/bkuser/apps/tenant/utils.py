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

import logging
from typing import Dict, Tuple

from bkuser.apps.data_source.models import DataSource, DataSourceDepartment, DataSourceUser
from bkuser.apps.tenant.constants import TenantUserIdRuleEnum
from bkuser.apps.tenant.models import TenantDepartmentIDRecord, TenantUserIDGenerateConfig, TenantUserIDRecord
from bkuser.utils.nanoid import generate_nanoid
from bkuser.utils.uuid import generate_uuid

logger = logging.getLogger(__name__)


def is_username_frozen(data_source: DataSource) -> bool:
    """数据源用户名是否不可变更"""
    return (
        TenantUserIDGenerateConfig.objects.filter(data_source=data_source)
        .exclude(rule=TenantUserIdRuleEnum.UUID4_HEX)
        .exclude(rule=TenantUserIdRuleEnum.NANOID)
        .exists()
    )


class TenantUserIDGenerator:
    """租户用户 ID 生成器"""

    def __init__(self, target_tenant_id: str, data_source: DataSource, prepare_batch: bool = False):
        """
        :param target_tenant_id: 目标租户 ID
        :param data_source: 数据源
        :param prepare_batch: 是否为批量生成做准备（预先生成租户用户 ID 映射表）
        """
        self.target_tenant_id = target_tenant_id
        self.data_source = data_source
        self.cfg = TenantUserIDGenerateConfig.objects.filter(
            target_tenant_id=target_tenant_id, data_source=data_source
        ).first()

        self.prepare_batch = prepare_batch
        # 租户用户 ID 映射表：{(tenant_id, data_source_id, code): tenant_user_id}
        self.tenant_user_id_map: Dict[Tuple[str, int, int], str] = {}
        if prepare_batch:
            self.tenant_user_id_map = {
                (target_tenant_id, data_source.id, record.code): record.tenant_user_id
                for record in TenantUserIDRecord.objects.filter(tenant_id=target_tenant_id, data_source=data_source)
            }

    def gen(self, user: DataSourceUser) -> str:
        """生成租户用户 ID"""
        if not self.cfg:
            return self._reuse_or_generate_id(user, TenantUserIdRuleEnum.NANOID)

        if self.cfg.rule == TenantUserIdRuleEnum.UUID4_HEX:
            return self._reuse_or_generate_id(user, TenantUserIdRuleEnum.UUID4_HEX)

        if self.cfg.rule == TenantUserIdRuleEnum.USERNAME_WITH_DOMAIN:
            return f"{user.username}@{self.cfg.domain}"

        if self.cfg.rule == TenantUserIdRuleEnum.USERNAME:
            return user.username

        return self._reuse_or_generate_id(user, TenantUserIdRuleEnum.NANOID)

    def _reuse_or_generate_id(self, user: DataSourceUser, rule: TenantUserIdRuleEnum) -> str:
        if self.prepare_batch:
            # 有准备的，直接从映射表里面查询
            if user_id := self.tenant_user_id_map.get((self.target_tenant_id, self.data_source.id, user.code)):
                return user_id
        else:
            # 没有准备的需现查 DB，没有的话就创建并生成
            record = TenantUserIDRecord.objects.filter(
                tenant_id=self.target_tenant_id, data_source=self.data_source, code=user.code
            ).first()
            if record and record.tenant_user_id:
                return record.tenant_user_id

        if rule == TenantUserIdRuleEnum.NANOID:
            tenant_user_id = generate_nanoid()
        else:
            tenant_user_id = generate_uuid()

        TenantUserIDRecord.objects.create(
            tenant_id=self.target_tenant_id,
            data_source_id=self.data_source.id,
            code=user.code,
            tenant_user_id=tenant_user_id,
        )
        return tenant_user_id


class TenantDeptIDGenerator:
    """租户部门 ID 生成器"""

    def __init__(self, target_tenant_id: str, data_source: DataSource, prepare_batch: bool = False):
        self.target_tenant_id = target_tenant_id
        self.data_source = data_source

        self.prepare_batch = prepare_batch
        # 租户部门 ID 映射表：{(tenant_id, data_source_id, code): tenant_dept_id}
        self.tenant_dept_id_map: Dict[Tuple[str, int, int], int] = {}
        if prepare_batch:
            self.tenant_dept_id_map = {
                (target_tenant_id, data_source.id, record.code): record.tenant_department_id
                for record in TenantDepartmentIDRecord.objects.filter(
                    tenant_id=target_tenant_id, data_source=data_source
                )
            }

    def gen(self, dept: DataSourceDepartment) -> int | None:
        """生成租户部门 ID，没有历史记录，则返回 None，由 DB 生成自增 ID"""
        if self.prepare_batch:
            # 有准备的，直接从映射表里面查询
            if dept_id := self.tenant_dept_id_map.get((self.target_tenant_id, self.data_source.id, dept.code)):
                return dept_id
        else:
            # 没有准备的需现查 DB，没有的话就创建并生成
            record = TenantDepartmentIDRecord.objects.filter(
                tenant_id=self.target_tenant_id, data_source=self.data_source, code=dept.code
            ).first()
            if record and record.tenant_department_id:
                return record.tenant_department_id

        return None
