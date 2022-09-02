# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.utils.translation import ugettext_lazy as _
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import (
    DepartmentCreatedReturnSerializer,
    DepartmentCreateSerializer,
    DepartmentSearchResultSerializer,
    DepartmentSearchSerializer,
)
from bkuser_core.api.web.utils import get_category, get_default_category_id, get_department, get_username
from bkuser_core.api.web.viewset import CustomPagination
from bkuser_core.bkiam.permissions import IAMAction, ManageDepartmentPermission, Permission
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.error_codes import error_codes
from bkuser_core.departments.models import Department
from bkuser_core.departments.signals import post_department_create


class DepartmentListCreateApi(generics.ListCreateAPIView):
    def create(self, request, *args, **kwargs):
        serializer = DepartmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # FIXME: category_id is required, can remove this check?
        category_id = data.get("category_id")
        if not category_id:
            category_id = get_default_category_id()
        else:
            if not ProfileCategory.objects.check_writable(category_id):
                raise error_codes.CANNOT_MANUAL_WRITE_INTO

        # category = ProfileCategory.objects.get(id=category_id)
        username = get_username(request)
        category = get_category(category_id)

        dept = {
            "name": data["name"],
            "category_id": category_id,
        }

        parent_id = data.get("parent")
        if parent_id:
            department = get_department(parent_id)
            Permission().allow_category_action(username, IAMAction.MANAGE_DEPARTMENT, department)

            dept.update({"parent": department, "order": department.get_max_order_in_children() + 1})
        else:
            Permission().allow_category_action(username, IAMAction.MANAGE_CATEGORY, category)
            # 不传 parent 默认为根部门
            data["level"] = 0
            max_order = list(
                Department.objects.filter(enabled=True, category_id=category_id, level=0).values_list(
                    "order", flat=True
                )
            )
            max_order = max(max_order or [0])
            dept.update({"level": 0, "order": max_order + 1})

        # 同一个组织下，不能有同名子部门
        try:
            instance = Department.objects.get(
                parent_id=parent_id,
                name=data["name"],
                category_id=category_id,
            )
            # 若是已删除的，将直接启用，未删除的抛出重复错误
            if not instance.enabled:
                instance.enable()
            else:
                raise error_codes.DEPARTMENT_NAME_CONFLICT
        except Department.DoesNotExist:
            instance = Department.objects.create(**dept)

        post_department_create.send(
            sender=self, instance=instance, operator=username, extra_values={"request": request}
        )
        return Response(DepartmentCreatedReturnSerializer(instance).data, status=status.HTTP_201_CREATED)


class DepartmentUpdateDeleteApi(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = "id"
    queryset = Department.objects.all()

    permission_classes = [ManageDepartmentPermission]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        # 当组织存在下级时无法删除
        if instance.children.filter(enabled=True).exists():
            # children.filter(enabled=True)
            raise error_codes.CANNOT_DELETE_DEPARTMENT.f(_("当前部门存在下级组织无法删除"))

        if instance.get_profiles().exists():
            raise error_codes.CANNOT_DELETE_DEPARTMENT.f(_("当前部门下存在用户无法删除"))

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DepartmentSearchApi(generics.ListAPIView):

    serializer_class = DepartmentSearchResultSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        serializer = DepartmentSearchSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        category_id = data.get("category_id")

        username = get_username(self.request)
        category = get_category(category_id)
        Permission().allow_category_action(username, IAMAction.VIEW_CATEGORY, category)

        # NOTE: 这里相对原来/api/v3/departments/?category_id 的差异是 enabled=True
        return Department.objects.filter(category_id=category_id, enabled=True)
