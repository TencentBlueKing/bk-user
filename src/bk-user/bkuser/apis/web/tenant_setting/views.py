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
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apis.web.tenant_setting.serializers import (
    TenantUserCustomFieldCreateInputSLZ,
    TenantUserCustomFieldCreateOutputSLZ,
    TenantUserCustomFieldUpdateInputSLZ,
    TenantUserFieldOutputSLZ,
    TenantUserValidityPeriodConfigInputSLZ,
    TenantUserValidityPeriodConfigOutputSLZ,
)
from bkuser.apps.tenant.models import (
    TenantManager,
    TenantUserCustomField,
    TenantUserValidityPeriodConfig,
    UserBuiltinField,
)
from bkuser.common.error_codes import error_codes
from bkuser.common.views import ExcludePatchAPIViewMixin, ExcludePutAPIViewMixin


class TenantUserFieldListApi(CurrentUserTenantMixin, generics.ListAPIView):
    pagination_class = None
    serializer_class = TenantUserFieldOutputSLZ

    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="用户字段列表",
        responses={status.HTTP_200_OK: TenantUserFieldOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant_id = self.get_current_tenant_id()

        slz = TenantUserFieldOutputSLZ(
            instance={
                "builtin_fields": UserBuiltinField.objects.all(),
                "custom_fields": TenantUserCustomField.objects.filter(tenant_id=tenant_id),
            }
        )
        return Response(slz.data)


class TenantUserCustomFieldCreateApi(CurrentUserTenantMixin, generics.CreateAPIView):
    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="新建用户自定义字段",
        request_body=TenantUserCustomFieldCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: TenantUserCustomFieldCreateOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        tenant_id = self.get_current_tenant_id()
        slz = TenantUserCustomFieldCreateInputSLZ(data=request.data, context={"tenant_id": tenant_id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        user_custom_field = TenantUserCustomField.objects.create(tenant_id=tenant_id, **data)
        return Response(
            TenantUserCustomFieldCreateOutputSLZ(instance={"id": user_custom_field.id}).data,
            status=status.HTTP_201_CREATED,
        )


class TenantUserCustomFieldUpdateDeleteApi(
    CurrentUserTenantMixin, ExcludePutAPIViewMixin, generics.UpdateAPIView, generics.DestroyAPIView
):
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return TenantUserCustomField.objects.filter(tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="修改用户自定义字段",
        request_body=TenantUserCustomFieldUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        tenant_id = self.get_current_tenant_id()

        slz = TenantUserCustomFieldUpdateInputSLZ(
            data=request.data, context={"tenant_id": tenant_id, "current_custom_field_id": kwargs["id"]}
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        custom_field = self.get_object()

        custom_field.display_name = data["display_name"]
        custom_field.required = data["required"]
        custom_field.default = data["default"]
        custom_field.options = data["options"]
        custom_field.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="删除用户自定义字段",
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class TenantUserValidityPeriodConfigRetrieveUpdateApi(
    ExcludePatchAPIViewMixin, CurrentUserTenantMixin, generics.RetrieveUpdateAPIView
):
    queryset = TenantUserValidityPeriodConfig.objects.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {"tenant_id": self.get_current_tenant_id()}
        return get_object_or_404(queryset, **filter_kwargs)

    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="当前租户的账户有效期配置",
        responses={
            status.HTTP_200_OK: TenantUserValidityPeriodConfigOutputSLZ(),
        },
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(TenantUserValidityPeriodConfigOutputSLZ(instance).data)

    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="更新当前租户的账户有效期配置",
        request_body=TenantUserValidityPeriodConfigInputSLZ(),
        responses={
            status.HTTP_204_NO_CONTENT: "",
        },
    )
    def put(self, request, *args, **kwargs):
        instance = self.get_object()

        # TODO (su) 权限调整为 perm_class 当前租户的管理才可做更新操作
        operator = request.user.username
        if not TenantManager.objects.filter(tenant_id=instance.tenant_id, tenant_user_id=operator).exists():
            raise error_codes.NO_PERMISSION

        slz = TenantUserValidityPeriodConfigInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        instance.enabled = data["enabled"]
        instance.validity_period = data["validity_period"]
        instance.remind_before_expire = data["remind_before_expire"]
        instance.enabled_notification_methods = data["enabled_notification_methods"]
        instance.notification_templates = data["notification_templates"]
        instance.updater = operator

        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
