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

from typing import Dict

from .constants import OperationTarget, OperationType
from .models import OperationAuditRecord


def add_operation_audit_record(
    operator: str,
    operation_target: OperationTarget,
    operation_type: OperationType,
    tenant_id: str,
    data_change: Dict | None = None,
    data_source_id: str | None = None,
    extras: Dict | None = None,
) -> OperationAuditRecord:
    return OperationAuditRecord.objects.create(
        creator=operator,
        operation_target=operation_target,
        operation_type=operation_type,
        tenant_id=tenant_id,
        data_change=data_change,
        data_source_id=data_source_id,
        extras=extras,
    )
