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
    TenantUserBuiltinFieldUpdateInputSLZ,
    TenantUserCustomFieldCreateInputSLZ,
    TenantUserCustomFieldUpdateInputSLZ,
    TenantUserDisplayNameExpressionConfigPreviewInputSLZ,
    TenantUserDisplayNameExpressionConfigPreviewOutputSLZ,
    TenantUserDisplayNameExpressionConfigRetrieveOutputSLZ,
    TenantUserDisplayNameExpressionConfigUpdateInputSLZ,
    TenantUserFieldOutputSLZ,
    TenantUserValidityPeriodConfigInputSLZ,
    TenantUserValidityPeriodConfigOutputSLZ,
)
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.tasks import (
    migrate_user_extras_with_mapping,
    remove_dropped_field_in_data_source_field_mapping,
    remove_dropped_field_in_user_extras,
)
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.models import (
    TenantUser,
    TenantUserBuiltinField,
    TenantUserCustomField,
    TenantUserDisplayNameExpressionConfig,
    TenantUserValidityPeriodConfig,
)
from bkuser.apps.tenant.tasks import remove_dropped_field_in_collaboration_strategy_field_mapping
from bkuser.biz.auditor import (
    TenantUserDisplayNameExpressionConfigUpdateAuditor,
    TenantUserValidityPeriodConfigUpdateAuditor,
)
from bkuser.biz.tenant import TenantUserBuiltinFieldHandler, TenantUserDisplayNameHandler
from bkuser.common.error_codes import error_codes
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
                "builtin_fields": TenantUserBuiltinField.objects.filter(tenant_id=tenant_id),
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

        # 【审计】创建租户账号有效期配置审计对象并记录变更前的数据
        auditor = TenantUserValidityPeriodConfigUpdateAuditor(request.user.username, self.get_current_tenant_id())

        cfg = self.get_object()
        auditor.pre_record_data_before(cfg)
        cfg.enabled = data["enabled"]
        cfg.validity_period = data["validity_period"]
        cfg.remind_before_expire = data["remind_before_expire"]
        cfg.enabled_notification_methods = data["enabled_notification_methods"]
        cfg.notification_templates = data["notification_templates"]
        cfg.updater = request.user.username
        cfg.save()

        # 【审计】记录变更后的数据
        auditor.record(cfg)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserDisplayNameExpressionConfigRetrieveUpdateApi(
    ExcludePatchAPIViewMixin, CurrentUserTenantMixin, generics.RetrieveUpdateAPIView
):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    def get_object(self):
        queryset = TenantUserDisplayNameExpressionConfig.objects.all()
        filter_kwargs = {"tenant_id": self.get_current_tenant_id()}
        return get_object_or_404(queryset, **filter_kwargs)

    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="用户展示名表达式配置",
        responses={status.HTTP_200_OK: TenantUserDisplayNameExpressionConfigRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        config = self.get_object()
        return Response(TenantUserDisplayNameExpressionConfigRetrieveOutputSLZ(instance=config).data)

    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="更新当前租户的用户展示名表达式配置",
        request_body=TenantUserDisplayNameExpressionConfigUpdateInputSLZ(),
        responses={
            status.HTTP_204_NO_CONTENT: "",
        },
    )
    def put(self, request, *args, **kwargs):
        tenant_id = self.get_current_tenant_id()
        slz = TenantUserDisplayNameExpressionConfigUpdateInputSLZ(data=request.data, context={"tenant_id": tenant_id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 从表达式中解析字段
        fields = TenantUserDisplayNameHandler.parse_display_name_expression(tenant_id, data["expression"])

        # 【审计】创建租户用户显示名称表达式配置审计对象并记录变更前的数据
        auditor = TenantUserDisplayNameExpressionConfigUpdateAuditor(request.user.username, tenant_id)

        config = self.get_object()
        auditor.pre_record_data_before(config)
        # 若表达式发生变化，则更新版本号
        if config.expression != data["expression"]:
            config.version += 1
        config.expression = data["expression"]
        config.fields = fields
        config.save()

        # 【审计】记录变更后的数据
        auditor.record(config)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserDisplayNameExpressionConfigPreviewApi(CurrentUserTenantMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="预览用户展示名（根据给定的展示名配置）",
        request_body=TenantUserDisplayNameExpressionConfigPreviewInputSLZ(),
        responses={
            status.HTTP_200_OK: TenantUserDisplayNameExpressionConfigPreviewOutputSLZ(many=True),
        },
    )
    def post(self, request, *args, **kwargs):
        tenant_id = self.get_current_tenant_id()
        slz = TenantUserDisplayNameExpressionConfigPreviewInputSLZ(data=request.data, context={"tenant_id": tenant_id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 从表达式中解析字段
        fields = TenantUserDisplayNameHandler.parse_display_name_expression(tenant_id, data["expression"])

        # 取前三个租户用户进行预览
        tenant_users = TenantUser.objects.filter(
            tenant_id=tenant_id, data_source__owner_tenant_id=tenant_id, data_source__type=DataSourceTypeEnum.REAL
        ).select_related("data_source_user", "data_source")[:3]

        config = TenantUserDisplayNameExpressionConfig(expression=data["expression"], fields=fields)

        if not tenant_users:
            # 如果目前没有获取到 tenant_user 则根据一个默认的租户用户进行生成 display_name
            default_tenant_user = TenantUserDisplayNameHandler.build_default_preview_tenant_user(tenant_id)
            display_name = TenantUserDisplayNameHandler.render_display_name(default_tenant_user, config)
            return Response(
                TenantUserDisplayNameExpressionConfigPreviewOutputSLZ([{"display_name": display_name}], many=True).data
            )

        user_display_names = [
            {"display_name": TenantUserDisplayNameHandler.render_display_name(user, config)} for user in tenant_users
        ]

        return Response(TenantUserDisplayNameExpressionConfigPreviewOutputSLZ(user_display_names, many=True).data)


class TenantUserBuiltinFieldUpdateApi(CurrentUserTenantMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return TenantUserBuiltinField.objects.filter(tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="更新当前租户的内置字段配置",
        request_body=TenantUserBuiltinFieldUpdateInputSLZ(),
        responses={
            status.HTTP_204_NO_CONTENT: "",
        },
    )
    def put(self, request, *args, **kwargs):
        tenant_id = self.get_current_tenant_id()
        slz = TenantUserBuiltinFieldUpdateInputSLZ(
            data=request.data, context={"tenant_id": tenant_id, "builtin_field_id": kwargs["id"]}
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        builtin_field = self.get_object()

        # 对字段配置中的唯一与必填属性进行校验
        self._validate_builtin_field_required(tenant_id, builtin_field, data["required"])
        self._validate_builtin_field_unique(tenant_id, builtin_field, data["unique"])

        builtin_field.required = data["required"]
        builtin_field.unique = data["unique"]
        builtin_field.personal_center_visible = data["personal_center_visible"]
        builtin_field.personal_center_editable = data["personal_center_editable"]
        builtin_field.manager_editable = data["manager_editable"]
        builtin_field.updater = request.user.username
        builtin_field.save(
            update_fields=[
                "required",
                "unique",
                "personal_center_visible",
                "personal_center_editable",
                "manager_editable",
                "updater",
            ]
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _summarize_error_user_names(usernames: list[str], limit: int = 5) -> str:
        # 整理异常的用户名列表为字符串信息，最多展示 `limit` 个用户名
        if not usernames:
            return ""

        message = ", ".join(usernames[:limit])
        if len(usernames) <= limit:
            return message

        return f"{message} 等 {len(usernames)} 个用户"

    def _validate_builtin_field_required(self, tenant_id: str, builtin_field: TenantUserBuiltinField, required: bool):
        # 如果要将字段设为必填，需要检查现有用户是否都有该字段的值
        if required:
            missing_users = TenantUserBuiltinFieldHandler.get_users_with_missing_field_value(
                tenant_id, builtin_field.name
            )
            if missing_users:
                user_list = self._summarize_error_user_names(missing_users)
                error_msg = (
                    f"无法将字段 '{builtin_field.name}' 设为必填："
                    f"{user_list} 未填写该字段的值。请先完善这些用户的字段数据。"
                )
                raise error_codes.TENANT_SETTING_BUILTIN_FIELD_REQUIRED_CHECK_FAILED.f(error_msg)
            return

        if builtin_field.name not in ["email", "phone"]:
            return

        # 如果要将 email 或 phone 设为非必填，检查另一个字段是否为必填
        target_field_name = "phone" if builtin_field.name == "email" else "email"
        target_field = TenantUserBuiltinField.objects.filter(tenant_id=tenant_id, name=target_field_name).first()
        if not target_field.required:
            raise error_codes.TENANT_SETTING_BUILTIN_FIELD_REQUIRED_CHECK_FAILED.f(
                f"无法将字段 '{builtin_field.name}' 设为非必填：另一个字段 '{target_field_name}' 已为非必填。"
            )

    def _validate_builtin_field_unique(self, tenant_id: str, builtin_field: TenantUserBuiltinField, unique: bool):
        if not unique:
            return

        # 如果要将字段设为唯一，需要检查现有用户该字段是否存在重复值
        duplicate_users = TenantUserBuiltinFieldHandler.get_users_with_duplicate_field_value(
            tenant_id, builtin_field.name
        )
        if duplicate_users:
            user_list = self._summarize_error_user_names(duplicate_users)
            error_msg = (
                f"无法将字段 '{builtin_field.name}' 设为唯一：" f"{user_list} 存在重复的字段值。请先修正这些重复数据。"
            )
            raise error_codes.TENANT_SETTING_BUILTIN_FIELD_UNIQUENESS_CHECK_FAILED.f(error_msg)
