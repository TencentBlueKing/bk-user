# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from typing import Dict, List, Optional, Union

from django.db import transaction

from bkuser.utils.uuid import generate_uuid

from .constants import ObjectType, Operation
from .models import OperationAuditRecord


def add_operation_audit_record(
    operator: str,
    tenant_id: str,
    operation: Operation,
    object_type: ObjectType,
    object_id: str,
    extras: Dict | None = None,
) -> OperationAuditRecord:
    return OperationAuditRecord.objects.create(
        creator=operator,
        tenant_id=tenant_id,
        operation=operation,
        object_type=object_type,
        object_id=object_id,
        extras=extras,
    )


def add_batch_operation_audit_records(
    operator: str,
    tenant_id: str,
    operation: Operation,
    object_type: ObjectType,
    object_ids: List[str],
    extras: Optional[Union[Dict, List]] = None,
) -> List[OperationAuditRecord]:
    records = []
    event_id = generate_uuid()

    if isinstance(extras, list):
        if len(extras) != len(object_ids):
            raise ValueError("The length of extras list must match the length of object_ids.")
        extras_list = extras
    else:
        # 如果 extras 是一个字典或 None，则批量操作的对象使用同一个 extras
        extras_list = [extras] * len(object_ids)

    for object_id, object_extras in zip(object_ids, extras_list):
        records.append(
            OperationAuditRecord(
                creator=operator,
                event_id=event_id,
                tenant_id=tenant_id,
                operation=operation,
                object_type=object_type,
                object_id=object_id,
                extras=object_extras,
            )
        )

    with transaction.atomic():
        OperationAuditRecord.objects.bulk_create(records)

    return records
