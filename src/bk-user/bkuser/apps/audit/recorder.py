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

from typing import Any, Dict, List, Optional

from bkuser.utils.uuid import generate_uuid

from .constants import ObjectTypeEnum, OperationEnum
from .data_models import AuditObject
from .models import OperationAuditRecord


def add_audit_record(
    operator: str,
    tenant_id: str,
    operation: OperationEnum,
    object_type: ObjectTypeEnum,
    object_id: str | int,
    object_name: str = "",
    data_before: Optional[Dict[str, Any]] = None,
    data_after: Optional[Dict[str, Any]] = None,
    extras: Optional[Dict[str, Any]] = None,
):
    """
    添加操作审计记录

    :param operator: 操作者
    :param tenant_id: 租户 ID
    :param operation: 操作行为
    :param object_type: 操作对象类型
    :param object_id: 操作对象 ID
    :param object_name: 操作对象名称
    :param data_before: 修改前数据
    :param data_after: 修改前数据
    :param extras: 额外相关数据
    """
    data_before = data_before or {}
    data_after = data_after or {}
    extras = extras or {}

    # 若有数据变更，则添加记录
    if data_before != data_after or extras:
        OperationAuditRecord.objects.create(
            creator=operator,
            tenant_id=tenant_id,
            operation=operation,
            object_type=object_type,
            object_id=str(object_id),
            object_name=object_name,
            data_before=data_before,
            data_after=data_after,
            extras=extras,
        )


def batch_add_audit_records(
    operator: str,
    tenant_id: str,
    objects: List[AuditObject],
):
    """
    批量添加操作审计记录

    :param operator: 操作者
    :param tenant_id: 租户 ID
    :param objects: AuditObject（包含操作对象相关信息）对象列表
    """
    # 生成事件 ID
    event_id = generate_uuid()

    records = [
        OperationAuditRecord(
            creator=operator,
            event_id=event_id,
            tenant_id=tenant_id,
            operation=obj.operation,
            object_type=obj.type,
            object_id=str(obj.id),
            object_name=obj.name,
            data_before=obj.data_before,
            data_after=obj.data_after,
            extras=obj.extras,
        )
        for obj in objects
        # 若有数据变更，则添加记录
        if obj.data_before != obj.data_after or obj.extras
    ]

    OperationAuditRecord.objects.bulk_create(records, batch_size=100)
