# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from typing import Any, Dict

from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.collaboration.serializers import (
    CollaborationFromStrategyConfirmInputSLZ,
    CollaborationFromStrategyListOutputSLZ,
    CollaborationFromStrategyTargetStatusUpdateOutputSLZ,
    CollaborationFromStrategyUpdateInputSLZ,
    CollaborationSourceTenantCustomFieldListOutputSLZ,
    CollaborationSyncRecordListOutputSLZ,
    CollaborationSyncRecordRetrieveOutputSLZ,
    CollaborationToStrategyCreateInputSLZ,
    CollaborationToStrategyCreateOutputSLZ,
    CollaborationToStrategyListOutputSLZ,
    CollaborationToStrategySourceStatusUpdateOutputSLZ,
    CollaborationToStrategyUpdateInputSLZ,
)
from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.sync.models import TenantSyncTask
from bkuser.apps.sync.shortcuts import start_collaboration_tenant_sync
from bkuser.apps.tenant.constants import CollaborationStrategyStatus
from bkuser.apps.tenant.models import (
    CollaborationStrategy,
    Tenant,
    TenantDepartment,
    TenantUser,
    TenantUserCustomField,
)
from bkuser.biz.tenant import TenantUserHandler
from bkuser.common.error_codes import error_codes
from bkuser.common.views import ExcludePatchAPIViewMixin

# --------------------------------------------- 分享方 API ---------------------------------------------


class CollaborationToStrategyListCreateApi(CurrentUserTenantMixin, generics.ListAPIView):
    """获取协同策略列表（分享方）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    serializer_class = CollaborationToStrategyListOutputSLZ
    pagination_class = None

    def get_queryset(self) -> QuerySet[CollaborationStrategy]:
        return CollaborationStrategy.objects.filter(source_tenant_id=self.get_current_tenant_id())

    def get_serializer_context(self) -> Dict[str, Any]:
        tenant_user_ids = self.get_queryset().values_list("creator", flat=True)
        return {
            "user_display_name_map": TenantUserHandler.get_tenant_user_display_name_map_by_ids(tenant_user_ids),
            "tenant_name_map": {t.id: t.name for t in Tenant.objects.all()},
        }

    @swagger_auto_schema(
        tags=["collaboration"],
        operation_description="获取协同策略列表（分享方）",
        responses={status.HTTP_200_OK: CollaborationToStrategyListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["collaboration"],
        operation_description="创建协同策略（分享方）",
        request_body=CollaborationToStrategyCreateInputSLZ,
        responses={status.HTTP_200_OK: CollaborationToStrategyCreateOutputSLZ(many=True)},
    )
    def post(self, request, *args, **kwargs):
        cur_tenant_id = self.get_current_tenant_id()
        slz = CollaborationToStrategyCreateInputSLZ(data=request.data, context={"tenant_id": cur_tenant_id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        strategy = CollaborationStrategy.objects.create(
            name=data["name"],
            source_tenant_id=cur_tenant_id,
            target_tenant_id=data["target_tenant_id"],
            source_config=data["source_config"],
            creator=request.user.username,
            updater=request.user.username,
        )
        return Response(data=CollaborationToStrategyCreateOutputSLZ(strategy).data, status=status.HTTP_201_CREATED)


class CollaborationToStrategyUpdateDestroyApi(
    CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.UpdateAPIView, generics.DestroyAPIView
):
    """编辑协同策略（分享方）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[CollaborationStrategy]:
        return CollaborationStrategy.objects.filter(source_tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["collaboration"],
        operation_description="编辑协同策略（分享方）",
        request_body=CollaborationToStrategyUpdateInputSLZ,
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = CollaborationToStrategyUpdateInputSLZ(
            data=request.data,
            context={
                "tenant_id": self.get_current_tenant_id(),
                "strategy_id": self.kwargs["id"],
            },
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        strategy = self.get_object()
        strategy.name = data["name"]
        strategy.source_config = data["source_config"]
        strategy.updater = request.user.username
        strategy.save(update_fields=["name", "source_config", "updater", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["collaboration"],
        operation_description="删除协同策略（分享方）",
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request, *args, **kwargs):
        strategy = self.get_object()
        if strategy.source_status != CollaborationStrategyStatus.DISABLED:
            raise error_codes.COLLABORATION_STRATEGY_DELETE_FAILED.f(_("删除前需要先停用协同策略"))

        with transaction.atomic():
            # 删除策略时，需要一并删除掉通过该策略产生的 TenantUser & TenantDepartment
            TenantUser.objects.filter(
                tenant=strategy.target_tenant,
                data_source__owner_tenant_id=strategy.source_tenant_id,
            ).delete()
            TenantDepartment.objects.filter(
                tenant=strategy.target_tenant,
                data_source__owner_tenant_id=strategy.source_tenant_id,
            ).delete()
            # 最后才是删除策略
            strategy.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CollaborationToStrategySourceStatusUpdateApi(
    CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.UpdateAPIView
):
    """协同策略更新状态（分享方）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[CollaborationStrategy]:
        return CollaborationStrategy.objects.filter(source_tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["collaboration"],
        operation_description="协同策略更新状态（分享方）",
        responses={status.HTTP_200_OK: CollaborationToStrategySourceStatusUpdateOutputSLZ()},
    )
    def put(self, request, *args, **kwargs):
        strategy = self.get_object()

        # 分享方的策略状态只有启用和禁用
        strategy.source_status = (
            CollaborationStrategyStatus.DISABLED
            if strategy.source_status == CollaborationStrategyStatus.ENABLED
            else CollaborationStrategyStatus.ENABLED
        )
        strategy.updater = request.user.username
        strategy.save(update_fields=["source_status", "updater", "updated_at"])

        # 分享方启用后，应该触发检查，如果两方都是启用，则需要执行同步（方法内已做检查）
        start_collaboration_tenant_sync(strategy)

        return Response(data=CollaborationToStrategySourceStatusUpdateOutputSLZ(strategy).data)


# --------------------------------------------- 接受方 API ---------------------------------------------


class CollaborationFromStrategyListApi(CurrentUserTenantMixin, generics.ListAPIView):
    """获取协同策略列表（接受方）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    serializer_class = CollaborationFromStrategyListOutputSLZ
    pagination_class = None

    def get_queryset(self) -> QuerySet[CollaborationStrategy]:
        return CollaborationStrategy.objects.filter(target_tenant_id=self.get_current_tenant_id())

    def get_serializer_context(self) -> Dict[str, Any]:
        return {"tenant_name_map": {t.id: t.name for t in Tenant.objects.all()}}

    @swagger_auto_schema(
        tags=["collaboration"],
        operation_description="获取协同策略列表（接受方）",
        responses={status.HTTP_200_OK: CollaborationFromStrategyListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CollaborationStrategySourceTenantCustomFieldListApi(
    CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.RetrieveAPIView
):
    """获取协同的源租户用户自定义字段列表（接受方）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[CollaborationStrategy]:
        return CollaborationStrategy.objects.filter(target_tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["collaboration"],
        operation_description="获取协同的源租户用户自定义字段列表（接受方）",
        responses={status.HTTP_200_OK: CollaborationSourceTenantCustomFieldListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        strategy = self.get_object()

        if strategy.source_status != CollaborationStrategyStatus.ENABLED:
            raise error_codes.COLLABORATION_STRATEGY_DISABLED_BY_SOURCE.f(_("无法获取分享方租户的自定义字段"))

        custom_fields = TenantUserCustomField.objects.filter(tenant=strategy.source_tenant).all()
        return Response(data=CollaborationSourceTenantCustomFieldListOutputSLZ(custom_fields, many=True).data)


class CollaborationFromStrategyUpdateApi(CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    """更新协同策略（接受方）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[CollaborationStrategy]:
        return CollaborationStrategy.objects.filter(target_tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["collaboration"],
        operation_description="更新协同策略（接受方）",
        request_body=CollaborationFromStrategyUpdateInputSLZ,
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        strategy = self.get_object()
        if strategy.target_status == CollaborationStrategyStatus.UNCONFIRMED:
            raise error_codes.COLLABORATION_STRATEGY_UPDATE_FAILED.f(_("该协同策略未确认，无法进行更新"))

        slz = CollaborationFromStrategyUpdateInputSLZ(
            data=request.data,
            context={
                "source_tenant_id": strategy.source_tenant_id,
                "target_tenant_id": self.get_current_tenant_id(),
            },
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        strategy.target_config = data["target_config"]
        strategy.updater = request.user.username
        strategy.save(update_fields=["target_config", "updater", "updated_at"])

        # 确认协同后，立即触发同步
        start_collaboration_tenant_sync(strategy)

        return Response(status=status.HTTP_204_NO_CONTENT)


class CollaborationFromStrategyConfirmApi(CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    """确认协同策略（接受方）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[CollaborationStrategy]:
        return CollaborationStrategy.objects.filter(target_tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["collaboration"],
        operation_description="确认协同策略（接受方）",
        request_body=CollaborationFromStrategyConfirmInputSLZ,
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        strategy = self.get_object()
        if strategy.target_status != CollaborationStrategyStatus.UNCONFIRMED:
            raise error_codes.COLLABORATION_STRATEGY_UPDATE_FAILED.f(_("该协同策略已确认，无需重复操作"))

        if strategy.source_status != CollaborationStrategyStatus.ENABLED:
            raise error_codes.COLLABORATION_STRATEGY_DISABLED_BY_SOURCE.f(
                _("无法进行确认，请联系分享方租户管理员启用该策略")
            )

        slz = CollaborationFromStrategyConfirmInputSLZ(
            data=request.data,
            context={
                "source_tenant_id": strategy.source_tenant_id,
                "target_tenant_id": self.get_current_tenant_id(),
            },
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        strategy.target_status = CollaborationStrategyStatus.ENABLED
        strategy.target_config = data["target_config"]
        strategy.updater = request.user.username
        strategy.save(update_fields=["target_status", "target_config", "updater", "updated_at"])

        # 确认协同后，立即触发同步
        start_collaboration_tenant_sync(strategy)

        return Response(status=status.HTTP_204_NO_CONTENT)


class CollaborationFromStrategyTargetStatusUpdateApi(
    CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.UpdateAPIView
):
    """协同策略更新状态（接受方）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[CollaborationStrategy]:
        return CollaborationStrategy.objects.filter(target_tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["collaboration"],
        operation_description="协同策略更新状态（接受方）",
        responses={status.HTTP_200_OK: CollaborationFromStrategyTargetStatusUpdateOutputSLZ()},
    )
    def put(self, request, *args, **kwargs):
        strategy = self.get_object()

        if strategy.target_status == CollaborationStrategyStatus.UNCONFIRMED:
            raise error_codes.COLLABORATION_STRATEGY_UPDATE_FAILED.f(_("请先确认策略，再尝试修改状态"))

        strategy.target_status = (
            CollaborationStrategyStatus.DISABLED
            if strategy.target_status == CollaborationStrategyStatus.ENABLED
            else CollaborationStrategyStatus.ENABLED
        )
        strategy.updater = request.user.username
        strategy.save(update_fields=["target_status", "updater", "updated_at"])

        # 接受方启用后，应该触发检查，如果两方都是启用，则需要执行同步（方法内已做检查）
        start_collaboration_tenant_sync(strategy)

        return Response(data=CollaborationFromStrategyTargetStatusUpdateOutputSLZ(strategy).data)


class CollaborationSyncRecordListApi(CurrentUserTenantMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    serializer_class = CollaborationSyncRecordListOutputSLZ

    def get_queryset(self) -> QuerySet[TenantSyncTask]:
        cur_tenant_id = self.get_current_tenant_id()
        return TenantSyncTask.objects.filter(tenant_id=cur_tenant_id).exclude(
            data_source__owner_tenant_id=cur_tenant_id
        )

    def get_serializer_context(self) -> Dict[str, Any]:
        return {"tenant_name_map": {t.id: t.name for t in Tenant.objects.all()}}

    @swagger_auto_schema(
        tags=["collaboration"],
        operation_description="协同策略同步记录列表",
        responses={status.HTTP_200_OK: CollaborationSyncRecordListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CollaborationSyncRecordRetrieveApi(CurrentUserTenantMixin, generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    serializer_class = CollaborationSyncRecordRetrieveOutputSLZ

    def get_queryset(self) -> QuerySet[TenantSyncTask]:
        cur_tenant_id = self.get_current_tenant_id()
        return TenantSyncTask.objects.filter(tenant_id=cur_tenant_id).exclude(
            data_source__owner_tenant_id=cur_tenant_id
        )

    @swagger_auto_schema(
        tags=["collaboration"],
        operation_description="协同策略同步记录详情",
        responses={status.HTTP_200_OK: CollaborationSyncRecordRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
