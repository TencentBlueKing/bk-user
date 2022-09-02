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
from rest_framework import generics, mixins, status
from rest_framework.response import Response

from .serializers import (
    DynamicFieldCreateSerializer,
    DynamicFieldUpdateSerializer,
    DynamicFieldUpdateVisibleSerializer,
    FieldSerializer,
)
from bkuser_core.bkiam.permissions import ManageFieldPermission
from bkuser_core.categories.signals import post_dynamic_field_delete
from bkuser_core.common.error_codes import error_codes
from bkuser_core.profiles.models import DynamicFieldInfo
from bkuser_core.profiles.signals import post_field_create


class FieldListCreateApi(generics.ListCreateAPIView):
    # FIXME: view_field permission for list api
    permission_classes = [ManageFieldPermission]
    serializer_class = FieldSerializer
    queryset = DynamicFieldInfo.objects.filter(enabled=True)

    # def get_queryset(self):
    #     queryset = DynamicFieldInfo.objects.filter(enabled=True)
    #     return queryset

    def create(self, request, *args, **kwargs):
        """创建自定义字段"""
        serializer = DynamicFieldCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # 默认加到最后
        order = validated_data.get("order", 0)
        if not order:
            validated_data["order"] = DynamicFieldInfo.objects.get_max_order() + 1

        instance = serializer.save()
        headers = self.get_success_headers(serializer.data)
        post_field_create.send(
            sender=self, instance=instance, operator=request.operator, extra_values={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class FieldManageableApi(generics.GenericAPIView):
    permission_classes = [ManageFieldPermission]

    def get(self, request):
        return Response({})


class FieldVisiableUpdateApi(generics.UpdateAPIView):
    permission_classes = [ManageFieldPermission]

    def patch(self, request, *args, **kwargs):
        slz = DynamicFieldUpdateVisibleSerializer(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data
        updating_ids = data["updating_ids"]

        # update all to False
        DynamicFieldInfo.objects.update(visible=False)
        # update current to True
        DynamicFieldInfo.objects.filter(id__in=updating_ids).update(visible=True)

        return Response({})


class FieldOrderUpdateApi(generics.UpdateAPIView):
    permission_classes = [ManageFieldPermission]

    lookup_url_kwarg = "id"
    queryset = DynamicFieldInfo.objects.all()

    def patch(self, request, *args, **kwargs):
        order = kwargs["order"]

        obj = self.get_object()
        obj.order = order
        # FIXME: here update_fields not working now
        obj.save(update_fields=["order"])

        return Response(FieldSerializer(obj).data)


class FieldUpdateDestroyApi(mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    permission_classes = [ManageFieldPermission]

    lookup_url_kwarg = "id"

    queryset = DynamicFieldInfo.objects.filter(enabled=True)
    serializer_class = DynamicFieldUpdateSerializer

    def update(self, request, *args, **kwargs):
        """更新自定义字段"""
        return self._update(request, partial=False)

    def partial_update(self, request, *args, **kwargs):
        """部分更新自定义字段"""
        return self._update(request, partial=True)

    def _update(self, request, partial):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

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
        return Response(FieldSerializer(instance).data)

    def destroy(self, request, *args, **kwargs):
        """移除自定义字段"""
        instance = self.get_object()
        # 内置字段不允许删除
        if instance.builtin:
            raise error_codes.BUILTIN_FIELD_CANNOT_BE_DELETED

        # 保证 order 密集
        DynamicFieldInfo.objects.filter(order__gt=instance.order).update(order=F("order") - 1)

        post_dynamic_field_delete.send(sender=self, instance=instance, operator=request.operator)

        # FIXME: 本来应该是204的, 但是前端目前根据是否200判定的 => 前端支持200/201/204判定状态
        # return super().destroy(request, *args, **kwargs)
        super().destroy(request, *args, **kwargs)
        return Response(status=status.HTTP_200_OK)
