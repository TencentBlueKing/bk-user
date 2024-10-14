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

from typing import Optional

from .models import OperationAuditRecord


def add_operation_audit_record(
    operator: str,
    target: str,
    operation: str,
    ip: Optional[str] = None,
    data_before: Optional[dict] = None,
    data_after: Optional[dict] = None,
    instance: Optional[dict] = None,
) -> OperationAuditRecord:
    return OperationAuditRecord.objects.create(
        operator=operator,
        target=target,
        operation=operation,
        ip=ip,
        data_before=data_before,
        data_after=data_after,
        instance=instance,
    )
