# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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
from typing import List

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.common.serializers import StringArrayField


def _validate_tenant_user_ids(user_ids: List[str], tenant_id: str, data_source_id: int) -> None:
    """校验租户用户 ID 列表中数据是否合法"""
    exists_tenant_users = TenantUser.objects.filter(
        id__in=user_ids, tenant_id=tenant_id, data_source_id=data_source_id
    )
    if invalid_user_ids := set(user_ids) - set(exists_tenant_users.values_list("id", flat=True)):
        raise ValidationError(_("用户 ID {} 在当前租户中不存在").format(", ".join(invalid_user_ids)))


def _validate_tenant_department_ids(department_ids: List[int], tenant_id: str, data_source_id: int) -> None:
    """校验租户部门 ID 列表中数据是否合法"""
    exists_tenant_depts = TenantDepartment.objects.filter(
        id__in=department_ids, tenant_id=tenant_id, data_source_id=data_source_id
    )
    if invalid_dept_ids := set(department_ids) - set(exists_tenant_depts.values_list("id", flat=True)):
        raise ValidationError(_("部门 ID {} 在当前租户中不存在").format(invalid_dept_ids))


class TenantDeptUserRelationBatchCreateInputSLZ(serializers.Serializer):
    """追加目标组织"""

    user_ids = serializers.ListField(
        help_text="用户 ID 列表",
        child=serializers.CharField(help_text="租户用户 ID"),
        min_length=1,
        max_length=settings.ORGANIZATION_BATCH_OPERATION_API_LIMIT,
    )
    target_department_ids = serializers.ListField(
        help_text="目标部门 ID 列表",
        child=serializers.IntegerField(help_text="目标部门 ID"),
        min_length=1,
        max_length=10,
    )

    def validate_user_ids(self, user_ids: List[str]) -> List[str]:
        _validate_tenant_user_ids(user_ids, self.context["tenant_id"], self.context["data_source_id"])
        return user_ids

    def validate_target_department_ids(self, department_ids: List[int]) -> List[int]:
        _validate_tenant_department_ids(department_ids, self.context["tenant_id"], self.context["data_source_id"])
        return department_ids


class TenantDeptUserRelationBatchUpdateInputSLZ(TenantDeptUserRelationBatchCreateInputSLZ):
    """清空并加入组织"""


class TenantDeptUserRelationBatchPatchInputSLZ(TenantDeptUserRelationBatchCreateInputSLZ):
    """移至目标组织"""

    source_department_id = serializers.IntegerField(help_text="当前部门 ID")

    def validate_source_department_id(self, department_id: int) -> int:
        _validate_tenant_department_ids([department_id], self.context["tenant_id"], self.context["data_source_id"])
        return department_id


class TenantDeptUserRelationBatchDeleteInputSLZ(serializers.Serializer):
    """移出当前组织"""

    user_ids = StringArrayField(
        help_text="用户 ID 列表", min_items=1, max_items=settings.ORGANIZATION_BATCH_OPERATION_API_LIMIT
    )
    source_department_id = serializers.IntegerField(help_text="当前部门 ID")

    def validate_user_ids(self, user_ids: List[str]) -> List[str]:
        _validate_tenant_user_ids(user_ids, self.context["tenant_id"], self.context["data_source_id"])
        return user_ids

    def validate_source_department_id(self, department_id: int) -> int:
        _validate_tenant_department_ids([department_id], self.context["tenant_id"], self.context["data_source_id"])
        return department_id
