# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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

from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from bkuser.apis.open_provider.constants import PROVIDER_BATCH_SIZE
from bkuser.apis.open_provider.mixins import ProviderApiCommonMixin
from bkuser.apis.open_provider.serializers.department import (
    DepartmentBatchCreateInputSLZ,
    DepartmentBatchDeleteInputSLZ,
    DepartmentBatchUpdateInputSLZ,
)
from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DepartmentRelationMPTTTree,
)
from bkuser.apps.tenant.models import TenantDepartment

logger = logging.getLogger(__name__)


class DepartmentBatchApi(ProviderApiCommonMixin, generics.GenericAPIView):
    """部门批量增删改"""

    BULK_CREATE_BATCH_SIZE = PROVIDER_BATCH_SIZE

    @swagger_auto_schema(
        tags=["open_provider.department"],
        operation_id="provider_batch_create_department",
        operation_description="批量创建部门",
        request_body=DepartmentBatchCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: ""},
    )
    def post(self, request, *args, **kwargs):
        slz = DepartmentBatchCreateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source = self.data_source
        tenant_id = self.tenant_id

        with transaction.atomic():
            for dept_info in data["departments"]:
                ds_dept = DataSourceDepartment.objects.create(
                    data_source=data_source,
                    code=dept_info["id"],
                    name=dept_info["name"],
                )

                # 默认创建为根部门，父子关系通过 department-relations 接口设置
                tree_record = DepartmentRelationMPTTTree.objects.create(data_source=data_source)
                DataSourceDepartmentRelation.objects.create(
                    department=ds_dept,
                    parent=None,
                    data_source=data_source,
                    tree_id=tree_record.id,
                )

                TenantDepartment.objects.create(
                    tenant_id=tenant_id,
                    data_source_department=ds_dept,
                    data_source=data_source,
                )

        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        tags=["open_provider.department"],
        operation_id="provider_batch_update_department",
        operation_description="批量更新部门",
        request_body=DepartmentBatchUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = DepartmentBatchUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source = self.data_source

        codes = [d["id"] for d in data["departments"]]
        ds_depts = DataSourceDepartment.objects.filter(data_source=data_source, code__in=codes)
        ds_dept_map = {d.code: d for d in ds_depts}

        with transaction.atomic():
            depts_to_update = []
            for dept_info in data["departments"]:
                ds_dept = ds_dept_map.get(dept_info["id"])
                if not ds_dept:
                    continue
                ds_dept.name = dept_info["name"]
                depts_to_update.append(ds_dept)

            if depts_to_update:
                DataSourceDepartment.objects.bulk_update(
                    depts_to_update, fields=["name", "updated_at"], batch_size=self.BULK_CREATE_BATCH_SIZE
                )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["open_provider.department"],
        operation_id="provider_batch_delete_department",
        operation_description="批量删除部门",
        request_body=DepartmentBatchDeleteInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request, *args, **kwargs):
        slz = DepartmentBatchDeleteInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source = self.data_source

        ds_depts = DataSourceDepartment.objects.filter(data_source=data_source, code__in=data["ids"])
        ds_dept_ids = list(ds_depts.values_list("id", flat=True))

        if not ds_dept_ids:
            return Response(status=status.HTTP_204_NO_CONTENT)

        has_children = DataSourceDepartmentRelation.objects.filter(parent__department_id__in=ds_dept_ids).exists()
        if has_children:
            raise ValidationError("cannot delete departments that have sub-departments")

        has_users = DataSourceDepartmentUserRelation.objects.filter(department_id__in=ds_dept_ids).exists()
        if has_users:
            raise ValidationError("cannot delete departments that have users")

        with transaction.atomic():
            TenantDepartment.objects.filter(data_source_department_id__in=ds_dept_ids).delete()
            DataSourceDepartmentRelation.objects.filter(department_id__in=ds_dept_ids).delete()
            DataSourceDepartment.objects.filter(id__in=ds_dept_ids).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
