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

from bkuser.apis.open_provider.mixins import ProviderApiCommonMixin
from bkuser.apis.open_provider.serializers.relation import (
    DepartmentRelationBatchInputSLZ,
    DepartmentUserRelationBatchCreateInputSLZ,
    DepartmentUserRelationBatchDeleteInputSLZ,
    UserLeaderRelationBatchCreateInputSLZ,
    UserLeaderRelationBatchDeleteInputSLZ,
)
from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)

logger = logging.getLogger(__name__)


class DepartmentRelationBatchApi(ProviderApiCommonMixin, generics.GenericAPIView):
    """部门父子关系批量设置"""

    @swagger_auto_schema(
        tags=["open_provider.relation"],
        operation_id="provider_batch_create_department_relation",
        operation_description="批量创建部门父子关系",
        request_body=DepartmentRelationBatchInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def post(self, request, *args, **kwargs):
        slz = DepartmentRelationBatchInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source = self.data_source

        all_codes = set()
        for rel in data["relations"]:
            all_codes.add(rel["id"])
            if rel["parent"]:
                all_codes.add(rel["parent"])

        dept_map = dict(
            DataSourceDepartment.objects.filter(data_source=data_source, code__in=all_codes).values_list("code", "id")
        )

        with transaction.atomic():
            for rel in data["relations"]:
                ds_dept_id = dept_map.get(rel["id"])
                if not ds_dept_id:
                    raise ValidationError(f"department with id '{rel['id']}' not found")

                dept_relation = DataSourceDepartmentRelation.objects.get(department_id=ds_dept_id)

                if not rel["parent"]:
                    dept_relation.move_to(None, position="first-child")
                else:
                    parent_ds_dept_id = dept_map.get(rel["parent"])
                    if not parent_ds_dept_id:
                        raise ValidationError(f"parent department with code '{rel['parent']}' not found")

                    parent_relation = DataSourceDepartmentRelation.objects.get(department_id=parent_ds_dept_id)
                    dept_relation.move_to(parent_relation, position="last-child")

        return Response(status=status.HTTP_204_NO_CONTENT)


class DepartmentUserRelationBatchApi(ProviderApiCommonMixin, generics.GenericAPIView):
    """用户-部门关系批量增删"""

    @swagger_auto_schema(
        tags=["open_provider.relation"],
        operation_id="provider_batch_create_department_user_relation",
        operation_description="批量创建用户-部门关系",
        request_body=DepartmentUserRelationBatchCreateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def post(self, request, *args, **kwargs):
        slz = DepartmentUserRelationBatchCreateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source = self.data_source

        user_codes = {rel["user_id"] for rel in data["relations"]}
        dept_codes = {rel["department_id"] for rel in data["relations"]}

        user_id_map = dict(
            DataSourceUser.objects.filter(data_source=data_source, code__in=user_codes).values_list("code", "id")
        )
        dept_id_map = dict(
            DataSourceDepartment.objects.filter(data_source=data_source, code__in=dept_codes).values_list("code", "id")
        )

        relations_to_create = []
        for rel in data["relations"]:
            ds_user_id = user_id_map.get(rel["user_id"])
            ds_dept_id = dept_id_map.get(rel["department_id"])
            if not ds_user_id or not ds_dept_id:
                continue

            relations_to_create.append(
                DataSourceDepartmentUserRelation(
                    user_id=ds_user_id,
                    department_id=ds_dept_id,
                    data_source=data_source,
                )
            )

        if relations_to_create:
            DataSourceDepartmentUserRelation.objects.bulk_create(relations_to_create, ignore_conflicts=True)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["open_provider.relation"],
        operation_id="provider_batch_delete_department_user_relation",
        operation_description="批量删除用户-部门关系",
        request_body=DepartmentUserRelationBatchDeleteInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request, *args, **kwargs):
        slz = DepartmentUserRelationBatchDeleteInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source = self.data_source

        user_codes = {rel["user_id"] for rel in data["relations"]}
        dept_codes = {rel["department_id"] for rel in data["relations"]}

        user_id_map = dict(
            DataSourceUser.objects.filter(data_source=data_source, code__in=user_codes).values_list("code", "id")
        )
        dept_id_map = dict(
            DataSourceDepartment.objects.filter(data_source=data_source, code__in=dept_codes).values_list("code", "id")
        )

        with transaction.atomic():
            for rel in data["relations"]:
                ds_user_id = user_id_map.get(rel["user_id"])
                ds_dept_id = dept_id_map.get(rel["department_id"])
                if not ds_user_id or not ds_dept_id:
                    continue

                DataSourceDepartmentUserRelation.objects.filter(user_id=ds_user_id, department_id=ds_dept_id).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserLeaderRelationBatchApi(ProviderApiCommonMixin, generics.GenericAPIView):
    """用户-Leader 关系批量增删"""

    @swagger_auto_schema(
        tags=["open_provider.relation"],
        operation_id="provider_batch_create_user_leader_relation",
        operation_description="批量覆盖用户-Leader关系（先删再建）",
        request_body=UserLeaderRelationBatchCreateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def post(self, request, *args, **kwargs):
        slz = UserLeaderRelationBatchCreateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source = self.data_source

        all_codes = set()
        for rel in data["relations"]:
            all_codes.add(rel["user_id"])
            all_codes.update(rel["leader_ids"])

        user_id_map = dict(
            DataSourceUser.objects.filter(data_source=data_source, code__in=all_codes).values_list("code", "id")
        )

        with transaction.atomic():
            for rel in data["relations"]:
                ds_user_id = user_id_map.get(rel["user_id"])
                if not ds_user_id:
                    continue

                leader_ds_user_ids = [user_id_map[code] for code in rel["leader_ids"] if code in user_id_map]

                DataSourceUserLeaderRelation.objects.filter(user_id=ds_user_id).delete()

                relations_to_create = [
                    DataSourceUserLeaderRelation(
                        user_id=ds_user_id,
                        leader_id=leader_id,
                        data_source=data_source,
                    )
                    for leader_id in leader_ds_user_ids
                ]
                if relations_to_create:
                    DataSourceUserLeaderRelation.objects.bulk_create(relations_to_create)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["open_provider.relation"],
        operation_id="provider_batch_delete_user_leader_relation",
        operation_description="批量删除用户-Leader关系",
        request_body=UserLeaderRelationBatchDeleteInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request, *args, **kwargs):
        slz = UserLeaderRelationBatchDeleteInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source = self.data_source

        all_codes = set()
        for rel in data["relations"]:
            all_codes.add(rel["user_id"])
            all_codes.update(rel["leader_ids"])

        user_id_map = dict(
            DataSourceUser.objects.filter(data_source=data_source, code__in=all_codes).values_list("code", "id")
        )

        with transaction.atomic():
            for rel in data["relations"]:
                ds_user_id = user_id_map.get(rel["user_id"])
                if not ds_user_id:
                    continue

                leader_ds_user_ids = [user_id_map[code] for code in rel["leader_ids"] if code in user_id_map]

                if leader_ds_user_ids:
                    DataSourceUserLeaderRelation.objects.filter(
                        user_id=ds_user_id, leader_id__in=leader_ds_user_ids
                    ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
