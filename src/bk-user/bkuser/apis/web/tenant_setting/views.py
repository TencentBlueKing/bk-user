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
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apis.web.tenant_setting.serializers import (
    TenantUserCustomFieldCreateInputSLZ,
    TenantUserCustomFieldUpdateInputSLZ,
    TenantUserFieldOutputSLZ,
    TenantUserValidityPeriodConfigInputSLZ,
    TenantUserValidityPeriodConfigOutputSLZ,
)
from bkuser.apps.audit.constants import ObjectTypeEnum, OperationEnum
from bkuser.apps.audit.recorder import add_audit_record
from bkuser.apps.data_source.tasks import (
    migrate_user_extras_with_mapping,
    remove_dropped_field_in_data_source_field_mapping,
    remove_dropped_field_in_user_extras,
)
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.models import (
    TenantUserCustomField,
    TenantUserValidityPeriodConfig,
    UserBuiltinField,
)
from bkuser.apps.tenant.tasks import remove_dropped_field_in_collaboration_strategy_field_mapping
from bkuser.common.views import ExcludePatchAPIViewMixin, ExcludePutAPIViewMixin


class TenantUserFieldListApi(CurrentUserTenantMixin, generics.ListAPIView):
    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]
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
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="新建用户自定义字段",
        request_body=TenantUserCustomFieldCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: ""},
    )
    def post(self, request, *args, **kwargs):
        tenant_id = self.get_current_tenant_id()
        slz = TenantUserCustomFieldCreateInputSLZ(data=request.data, context={"tenant_id": tenant_id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        TenantUserCustomField.objects.create(tenant_id=tenant_id, **data)
        return Response(status=status.HTTP_201_CREATED)


class TenantUserCustomFieldUpdateDeleteApi(
    CurrentUserTenantMixin, ExcludePutAPIViewMixin, generics.UpdateAPIView, generics.DestroyAPIView
):
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

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
            data=request.data, context={"tenant_id": tenant_id, "custom_field_id": kwargs["id"]}
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        custom_field = self.get_object()
        custom_field.display_name = data["display_name"]
        custom_field.default = data["default"]
        custom_field.options = data["options"]
        custom_field.save()

        # 修改自定义字段配置，可能会影响到现存的枚举/多选枚举类型字段数据，需要支持数据迁移
        if custom_field.data_type in [UserFieldDataType.ENUM, UserFieldDataType.MULTI_ENUM]:
            migrate_user_extras_with_mapping.delay(tenant_id, custom_field.name, data["mapping"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="删除用户自定义字段",
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request, *args, **kwargs):
        custom_field = self.get_object()
        tenant_id, field_name = custom_field.tenant_id, custom_field.name
        custom_field.delete()

        # 删除自定义字段，需要执行数据清理，包括数据源字段映射配置 + 租户协同策略字段映射 + 用户自定义字段数据
        remove_dropped_field_in_data_source_field_mapping.delay(tenant_id, field_name)
        remove_dropped_field_in_collaboration_strategy_field_mapping.delay(tenant_id, field_name)
        remove_dropped_field_in_user_extras.delay(tenant_id, field_name)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserValidityPeriodConfigRetrieveUpdateApi(
    ExcludePatchAPIViewMixin, CurrentUserTenantMixin, generics.RetrieveUpdateAPIView
):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    def get_object(self):
        queryset = TenantUserValidityPeriodConfig.objects.all()
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
        return Response(TenantUserValidityPeriodConfigOutputSLZ(instance=instance).data)

    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="更新当前租户的账户有效期配置",
        request_body=TenantUserValidityPeriodConfigInputSLZ(),
        responses={
            status.HTTP_204_NO_CONTENT: "",
        },
    )
    def put(self, request, *args, **kwargs):
        slz = TenantUserValidityPeriodConfigInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        cfg = self.get_object()

        # 【审计】记录变更前数据
        data_before = {
            "enabled": cfg.enabled,
            "validity_period": cfg.validity_period,
            "remind_before_expire": cfg.remind_before_expire,
            "enabled_notification_methods": cfg.enabled_notification_methods,
            "notification_templates": cfg.notification_templates,
        }

        cfg.enabled = data["enabled"]
        cfg.validity_period = data["validity_period"]
        cfg.remind_before_expire = data["remind_before_expire"]
        cfg.enabled_notification_methods = data["enabled_notification_methods"]
        cfg.notification_templates = data["notification_templates"]
        cfg.updater = request.user.username
        cfg.save()

        # 审计记录
        add_audit_record(
            operator=request.user.username,
            tenant_id=self.get_current_tenant_id(),
            operation=OperationEnum.MODIFY_TENANT_ACCOUNT_VALIDITY_PERIOD_CONFIG,
            object_type=ObjectTypeEnum.TENANT,
            object_id=self.get_current_tenant_id(),
            extras={"data_before": data_before},
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
