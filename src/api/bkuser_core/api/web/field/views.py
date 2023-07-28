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

from django.db.models import F
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import (
    DynamicFieldCreateInputSLZ,
    DynamicFieldUpdateInputSLZ,
    DynamicFieldUpdateVisibleInputSLZ,
    FieldOutputSLZ,
)
from bkuser_core.audit.constants import OperationType
from bkuser_core.audit.utils import audit_general_log, create_general_log
from bkuser_core.bkiam.permissions import ManageFieldPermission
from bkuser_core.categories.signals import post_dynamic_field_delete
from bkuser_core.common.error_codes import error_codes
from bkuser_core.profiles.models import DynamicFieldInfo
from bkuser_core.profiles.signals import post_field_create


class FieldListCreateApi(generics.ListCreateAPIView):
    # FIXME: 目前无法加权限, 加上会导致前端先弹窗这个, 在弹窗真正需要申请的权限(因为页面同时加载了多个api), 非敏感信息
    # permission_classes = [ManageFieldPermission]
    serializer_class = FieldOutputSLZ
    queryset = DynamicFieldInfo.objects.filter(enabled=True)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # FIXME: 目前无法加权限, 加上会导致前端先弹窗这个, 在弹窗真正需要申请的权限(因为页面同时加载了多个api), 非敏感信息
        if self.request.method == "GET":
            return []
        return [ManageFieldPermission()]

    def create(self, request, *args, **kwargs):
        """创建自定义字段"""
        slz = DynamicFieldCreateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        validated_data = slz.validated_data

        # 默认加到最后
        order = validated_data.get("order", 0)
        if not order:
            validated_data["order"] = DynamicFieldInfo.objects.get_max_order() + 1

        instance = slz.save()
        headers = self.get_success_headers(slz.data)
        post_field_create.send(
            sender=self, instance=instance, operator=request.operator, extra_values={"request": request}
        )

        return Response(slz.data, status=status.HTTP_201_CREATED, headers=headers)


class FieldManageableApi(generics.GenericAPIView):
    permission_classes = [ManageFieldPermission]

    def get(self, request):
        return Response({})


class FieldVisiableUpdateApi(generics.UpdateAPIView):
    permission_classes = [ManageFieldPermission]

    def _add_fields_update_visible_audit_log(self, queryset, visible):
        visible_operate_type_map = {
            True: OperationType.SET_FIELD_VISIBLE.value,
            False: OperationType.SET_FIELD_INVISIBLE.value,
        }
        for item in queryset:
            create_general_log(
                operator=self.request.operator,
                operate_type=visible_operate_type_map[visible],
                operator_obj=item,
                request=self.request,
            )

    def patch(self, request, *args, **kwargs):
        slz = DynamicFieldUpdateVisibleInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data
        updating_ids = data["updating_ids"]

        # current visible fields
        current_visible_field_ids = DynamicFieldInfo.objects.filter(visible=True).values_list("id", flat=True)

        # to visible = False
        invisible_field_ids = set(current_visible_field_ids) - set(updating_ids)
        if invisible_field_ids:
            invisible_fields = DynamicFieldInfo.objects.filter(id__in=list(invisible_field_ids))
            invisible_fields.update(visible=False)
            self._add_fields_update_visible_audit_log(invisible_fields, visible=False)

        # to visible = True
        visible_field_ids = set(updating_ids) - set(current_visible_field_ids)
        if visible_field_ids:
            visible_fields = DynamicFieldInfo.objects.filter(id__in=list(visible_field_ids))
            visible_fields.update(visible=True)
            self._add_fields_update_visible_audit_log(visible_fields, visible=True)

        return Response({})


class FieldOrderUpdateApi(generics.UpdateAPIView):
    permission_classes = [ManageFieldPermission]

    lookup_url_kwarg = "id"
    queryset = DynamicFieldInfo.objects.all()

    @audit_general_log(operate_type=OperationType.UPDATE.value)
    def patch(self, request, *args, **kwargs):
        order = kwargs["order"]

        obj = self.get_object()
        DynamicFieldInfo.objects.update_order(obj, order)

        return Response(FieldOutputSLZ(obj).data)


class FieldUpdateDestroyApi(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [ManageFieldPermission]

    lookup_url_kwarg = "id"

    queryset = DynamicFieldInfo.objects.filter(enabled=True)
    serializer_class = DynamicFieldUpdateInputSLZ

    @audit_general_log(operate_type=OperationType.UPDATE.value)
    def put(self, request, *args, **kwargs):
        """更新自定义字段"""
        return self._update(request, partial=False)

    @audit_general_log(operate_type=OperationType.UPDATE.value)
    def patch(self, request, *args, **kwargs):
        """部分更新自定义字段"""
        return self._update(request, partial=True)

    def _update(self, request, partial):
        instance = self.get_object()
        slz = self.serializer_class(instance, data=request.data, partial=partial)
        slz.is_valid(raise_exception=True)
        validated_data = slz.validated_data

        # 内置字段 只能更新 order & visible
        if not instance.configurable and set(validated_data.keys()) - {
            "order",
            "visible",
        }:
            raise error_codes.FIELD_IS_NOT_EDITABLE.f("该字段无法更新")

        if "name" in validated_data:
            raise error_codes.FIELD_IS_NOT_EDITABLE.f("字段 key 值无法更新")

        updating_order = validated_data.get("order", False)
        if updating_order:
            """整理 order"""
            DynamicFieldInfo.objects.update_order(instance, updating_order)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return Response(FieldOutputSLZ(instance).data)

    def delete(self, request, *args, **kwargs):
        """移除自定义字段"""
        instance = self.get_object()
        # 内置字段不允许删除
        if instance.builtin:
            raise error_codes.BUILTIN_FIELD_CANNOT_BE_DELETED

        # 保证 order 密集
        DynamicFieldInfo.objects.filter(order__gt=instance.order).update(order=F("order") - 1)

        post_dynamic_field_delete.send(sender=self, instance=instance, operator=request.operator)

        super().destroy(request, *args, **kwargs)
        # NOTE: 本来应该是204的, 但是前端目前根据是否200+bk_response判定的; 204无内容
        return Response(status=status.HTTP_200_OK)
