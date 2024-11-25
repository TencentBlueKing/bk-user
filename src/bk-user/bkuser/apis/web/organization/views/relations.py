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

import itertools

from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.organization.serializers import (
    TenantDeptUserRelationBatchCreateInputSLZ,
    TenantDeptUserRelationBatchDeleteInputSLZ,
    TenantDeptUserRelationBatchPatchInputSLZ,
    TenantDeptUserRelationBatchUpdateInputSLZ,
)
from bkuser.apis.web.organization.views.mixins import CurrentUserTenantDataSourceMixin
from bkuser.apps.data_source.models import DataSourceDepartmentUserRelation
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.biz.auditor import TenantUserDepartmentRelationsAuditor


class TenantDeptUserRelationBatchCreateApi(CurrentUserTenantDataSourceMixin, generics.CreateAPIView):
    """批量添加 / 拉取租户用户（添加部门 - 用户关系）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["organization.user"],
        operation_description="租户用户 - 从其他组织拉取 / 添加到其他组织（仅添加关系）",
        request_body=TenantDeptUserRelationBatchCreateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def post(self, request, *args, **kwargs):
        cur_tenant_id = self.get_current_tenant_id()
        data_source = self.get_current_tenant_local_real_data_source()

        slz = TenantDeptUserRelationBatchCreateInputSLZ(
            data=request.data, context={"tenant_id": cur_tenant_id, "data_source_id": data_source.id}
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source_dept_ids = TenantDepartment.objects.filter(
            tenant_id=cur_tenant_id, id__in=data["target_department_ids"]
        ).values_list("data_source_department_id", flat=True)

        data_source_user_ids = TenantUser.objects.filter(
            tenant_id=cur_tenant_id,
            id__in=data["user_ids"],
        ).values_list("data_source_user_id", flat=True)

        # 【审计】创建审计对象并记录变更前的数据
        auditor = TenantUserDepartmentRelationsAuditor(
            operator=request.user.username, tenant_id=cur_tenant_id, data_source_user_ids=data_source_user_ids
        )
        auditor.pre_record_data_before()

        # 复制操作：为数据源部门 & 用户添加关联边，但是不会影响存量的关联边
        relations = [
            DataSourceDepartmentUserRelation(user_id=user_id, department_id=dept_id, data_source=data_source)
            for dept_id, user_id in itertools.product(data_source_dept_ids, data_source_user_ids)
        ]
        # 由于复制操作不会影响存量的关联边，所以需要忽略冲突，避免出现用户复选的情况
        DataSourceDepartmentUserRelation.objects.bulk_create(relations, ignore_conflicts=True)

        # 【审计】将审计记录保存至数据库
        auditor.batch_record()

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantDeptUserRelationBatchUpdateApi(CurrentUserTenantDataSourceMixin, generics.UpdateAPIView):
    """批量移动租户用户（更新部门 - 用户关系）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["organization.user"],
        operation_description="租户用户 - 清空并加入到其他组织（会删除当前所有关系）",
        request_body=TenantDeptUserRelationBatchUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        cur_tenant_id = self.get_current_tenant_id()
        data_source = self.get_current_tenant_local_real_data_source()

        slz = TenantDeptUserRelationBatchUpdateInputSLZ(
            data=request.data, context={"tenant_id": cur_tenant_id, "data_source_id": data_source.id}
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source_dept_ids = TenantDepartment.objects.filter(
            tenant_id=cur_tenant_id, id__in=data["target_department_ids"]
        ).values_list("data_source_department_id", flat=True)

        data_source_user_ids = TenantUser.objects.filter(
            tenant_id=cur_tenant_id,
            id__in=data["user_ids"],
        ).values_list("data_source_user_id", flat=True)

        # 【审计】创建审计对象并记录变更前的数据
        auditor = TenantUserDepartmentRelationsAuditor(
            operator=request.user.username, tenant_id=cur_tenant_id, data_source_user_ids=data_source_user_ids
        )
        auditor.pre_record_data_before()

        # 移动操作：为数据源部门 & 用户添加关联边，但是会删除这批用户所有的存量关联边
        with transaction.atomic():
            # 先删除
            DataSourceDepartmentUserRelation.objects.filter(user_id__in=data_source_user_ids).delete()
            # 再添加
            relations = [
                DataSourceDepartmentUserRelation(user_id=user_id, department_id=dept_id, data_source=data_source)
                for dept_id, user_id in itertools.product(data_source_dept_ids, data_source_user_ids)
            ]
            DataSourceDepartmentUserRelation.objects.bulk_create(relations)

        # 【审计】将审计记录保存至数据库
        auditor.batch_record(extras={"department_ids": list(data_source_dept_ids)})

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["organization.user"],
        operation_description="租户用户 - 移至其他组织（仅删除当前部门关系）",
        request_body=TenantDeptUserRelationBatchPatchInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def patch(self, request, *args, **kwargs):
        cur_tenant_id = self.get_current_tenant_id()
        data_source = self.get_current_tenant_local_real_data_source()

        slz = TenantDeptUserRelationBatchPatchInputSLZ(
            data=request.data, context={"tenant_id": cur_tenant_id, "data_source_id": data_source.id}
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        source_data_source_dept = TenantDepartment.objects.get(id=data["source_department_id"]).data_source_department

        data_source_dept_ids = TenantDepartment.objects.filter(
            tenant_id=cur_tenant_id, id__in=data["target_department_ids"]
        ).values_list("data_source_department_id", flat=True)

        data_source_user_ids = TenantUser.objects.filter(
            tenant_id=cur_tenant_id,
            id__in=data["user_ids"],
        ).values_list("data_source_user_id", flat=True)

        # 【审计】创建审计对象
        auditor = TenantUserDepartmentRelationsAuditor(
            operator=request.user.username, tenant_id=cur_tenant_id, data_source_user_ids=data_source_user_ids
        )
        auditor.pre_record_data_before()

        # 移动操作：为数据源部门 & 用户添加关联边，但是会删除这批用户在当前部门的存量关联边
        with transaction.atomic():
            # 先删除（仅限于指定部门）
            DataSourceDepartmentUserRelation.objects.filter(
                user_id__in=data_source_user_ids, department=source_data_source_dept
            ).delete()
            # 再添加
            relations = [
                DataSourceDepartmentUserRelation(user_id=user_id, department_id=dept_id, data_source=data_source)
                for dept_id, user_id in itertools.product(data_source_dept_ids, data_source_user_ids)
            ]
            DataSourceDepartmentUserRelation.objects.bulk_create(relations, ignore_conflicts=True)

        # 【审计】将审计记录保存至数据库
        auditor.batch_record(extras={"department_id": source_data_source_dept.id})

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantDeptUserRelationBatchDeleteApi(CurrentUserTenantDataSourceMixin, generics.DestroyAPIView):
    """批量删除指定部门 & 用户的部门 - 用户关系"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["organization.user"],
        operation_description="租户用户 - 移出当前组织（仅删除当前部门关系）",
        query_serializer=TenantDeptUserRelationBatchDeleteInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request, *args, **kwargs):
        cur_tenant_id = self.get_current_tenant_id()
        data_source = self.get_current_tenant_local_real_data_source()

        slz = TenantDeptUserRelationBatchDeleteInputSLZ(
            data=request.query_params, context={"tenant_id": cur_tenant_id, "data_source_id": data_source.id}
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        source_data_source_dept = TenantDepartment.objects.get(id=data["source_department_id"]).data_source_department

        data_source_user_ids = TenantUser.objects.filter(
            tenant_id=cur_tenant_id,
            id__in=data["user_ids"],
        ).values_list("data_source_user_id", flat=True)

        # 【审计】创建审计对象
        auditor = TenantUserDepartmentRelationsAuditor(
            operator=request.user.username, tenant_id=cur_tenant_id, data_source_user_ids=data_source_user_ids
        )
        auditor.pre_record_data_before()

        DataSourceDepartmentUserRelation.objects.filter(
            user_id__in=data_source_user_ids, department=source_data_source_dept
        ).delete()

        # 【审计】将审计记录保存至数据库
        auditor.batch_record(extras={"department_id": source_data_source_dept.id})

        return Response(status=status.HTTP_204_NO_CONTENT)
