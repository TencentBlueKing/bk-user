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
from typing import Any, Dict

from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.collaboration.serializers import (
    CollaborativeFromStrategyListOutputSLZ,
    CollaborativeStrategyConfirmInputSLZ,
    CollaborativeStrategyCreateInputSLZ,
    CollaborativeStrategyCreateOutputSLZ,
    CollaborativeStrategyStatusUpdateOutputSLZ,
    CollaborativeStrategyUpdateInputSLZ,
    CollaborativeSyncRecordListOutputSLZ,
    CollaborativeToStrategyListOutputSLZ,
)
from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.sync.models import TenantSyncTask
from bkuser.apps.tenant.constants import CollaborativeStrategyStatus
from bkuser.apps.tenant.models import CollaborativeStrategy, Tenant, TenantDepartment, TenantUser
from bkuser.biz.tenant import TenantUserHandler
from bkuser.common.error_codes import error_codes
from bkuser.common.views import ExcludePatchAPIViewMixin


class CollaborativeToStrategyListApi(CurrentUserTenantMixin, generics.ListAPIView):
    """获取协同策略列表（分享方）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    serializer_class = CollaborativeToStrategyListOutputSLZ
    pagination_class = None

    def get_queryset(self) -> QuerySet[CollaborativeStrategy]:
        return CollaborativeStrategy.objects.filter(source_tenant_id=self.get_current_tenant_id())

    def get_serializer_context(self) -> Dict[str, Any]:
        tenant_user_ids = self.get_queryset().values_list("creator", flat=True)
        return {
            "user_display_name_map": TenantUserHandler.get_tenant_user_display_name_map_by_ids(tenant_user_ids),
            "tenant_name_map": {t.id: t.name for t in Tenant.objects.all()},
        }

    @swagger_auto_schema(
        tags=["collaborative"],
        operation_description="获取协同策略列表（分享方）",
        responses={status.HTTP_200_OK: CollaborativeToStrategyListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CollaborativeFromStrategyListApi(CurrentUserTenantMixin, generics.ListAPIView):
    """获取协同策略列表（接受方）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    serializer_class = CollaborativeFromStrategyListOutputSLZ
    pagination_class = None

    def get_queryset(self) -> QuerySet[CollaborativeStrategy]:
        return CollaborativeStrategy.objects.filter(target_tenant_id=self.get_current_tenant_id())

    def get_serializer_context(self) -> Dict[str, Any]:
        return {"tenant_name_map": {t.id: t.name for t in Tenant.objects.all()}}

    @swagger_auto_schema(
        tags=["collaborative"],
        operation_description="获取协同策略列表（接受方）",
        responses={status.HTTP_200_OK: CollaborativeFromStrategyListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CollaborativeStrategyCreateApi(CurrentUserTenantMixin, generics.CreateAPIView):
    """创建协同策略（分享方）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["collaborative"],
        operation_description="创建协同策略（分享方）",
        request_body=CollaborativeStrategyCreateInputSLZ,
        responses={status.HTTP_200_OK: CollaborativeStrategyCreateOutputSLZ(many=True)},
    )
    def post(self, request, *args, **kwargs):
        cur_tenant_id = self.get_current_tenant_id()
        slz = CollaborativeStrategyCreateInputSLZ(data=request.data, context={"tenant_id": cur_tenant_id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        strategy = CollaborativeStrategy.objects.create(
            name=data["name"],
            source_tenant_id=cur_tenant_id,
            target_tenant_id=data["target_tenant_id"],
            source_config=data["config"],
            creator=request.user.username,
            updater=request.user.username,
        )
        return Response(data=CollaborativeStrategyCreateOutputSLZ(strategy).data, status=status.HTTP_201_CREATED)


class CollaborativeStrategyUpdateDestroyApi(
    CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.UpdateAPIView, generics.DestroyAPIView
):
    """编辑协同策略（分享方）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[CollaborativeStrategy]:
        return CollaborativeStrategy.objects.filter(source_tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["collaborative"],
        operation_description="编辑协同策略（分享方）",
        request_body=CollaborativeStrategyUpdateInputSLZ,
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = CollaborativeStrategyUpdateInputSLZ(
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
        strategy.source_config = data["config"]
        strategy.updater = request.user.username
        strategy.save(update_fields=["name", "source_config", "updater", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["collaborative"],
        operation_description="删除协同策略（分享方）",
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request, *args, **kwargs):
        strategy = self.get_object()

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


class CollaborativeStrategyConfirmApi(CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    """确认协同策略（接受方）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[CollaborativeStrategy]:
        return CollaborativeStrategy.objects.filter(target_tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["collaborative"],
        operation_description="确认协同策略（接受方）",
        request_body=CollaborativeStrategyConfirmInputSLZ,
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        strategy = self.get_object()
        if strategy.target_status != CollaborativeStrategyStatus.UNCONFIRMED:
            raise error_codes.COLLABORATIVE_STRATEGY_UPDATE_FAILED.f(_("该协同策略已确认，无需重复操作"))

        slz = CollaborativeStrategyConfirmInputSLZ(
            data=request.data, context={"tenant_id": self.get_current_tenant_id()}
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        strategy.target_status = CollaborativeStrategyStatus.ENABLED
        strategy.target_config = data["config"]
        strategy.updater = request.user.username
        strategy.save(update_fields=["target_status", "target_config", "updater", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class CollaborativeStrategySourceStatusUpdateApi(
    CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.UpdateAPIView
):
    """协同策略更新状态（分享方）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[CollaborativeStrategy]:
        return CollaborativeStrategy.objects.filter(source_tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["collaborative"],
        operation_description="协同策略更新状态（分享方）",
        responses={status.HTTP_200_OK: CollaborativeStrategyStatusUpdateOutputSLZ()},
    )
    def put(self, request, *args, **kwargs):
        strategy = self.get_object()

        # 分享方的策略状态只有启用和禁用
        strategy.source_status = (
            CollaborativeStrategyStatus.DISABLED
            if strategy.source_status == CollaborativeStrategyStatus.ENABLED
            else CollaborativeStrategyStatus.ENABLED
        )
        strategy.updater = request.user.username
        strategy.save(update_fields=["source_status", "updater", "updated_at"])

        return Response(
            data=CollaborativeStrategyStatusUpdateOutputSLZ({"status": strategy.source_status.value}).data,
            status=status.HTTP_200_OK,
        )


class CollaborativeStrategyTargetStatusUpdateApi(
    CurrentUserTenantMixin, ExcludePatchAPIViewMixin, generics.UpdateAPIView
):
    """协同策略更新状态（接受方）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"

    def get_queryset(self) -> QuerySet[CollaborativeStrategy]:
        return CollaborativeStrategy.objects.filter(target_tenant_id=self.get_current_tenant_id())

    @swagger_auto_schema(
        tags=["collaborative"],
        operation_description="协同策略更新状态（接受方）",
        responses={status.HTTP_200_OK: CollaborativeStrategyStatusUpdateOutputSLZ()},
    )
    def put(self, request, *args, **kwargs):
        strategy = self.get_object()

        if strategy.target_status == CollaborativeStrategyStatus.UNCONFIRMED:
            raise error_codes.COLLABORATIVE_STRATEGY_UPDATE_FAILED.f(_("请先确认策略，再尝试修改状态"))

        strategy.target_status = (
            CollaborativeStrategyStatus.DISABLED
            if strategy.target_status == CollaborativeStrategyStatus.ENABLED
            else CollaborativeStrategyStatus.ENABLED
        )
        strategy.updater = request.user.username
        strategy.save(update_fields=["target_status", "updater", "updated_at"])

        return Response(
            data=CollaborativeStrategyStatusUpdateOutputSLZ({"status": strategy.target_status.value}).data,
            status=status.HTTP_200_OK,
        )


class CollaborativeSyncRecordListApi(CurrentUserTenantMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    serializer_class = CollaborativeSyncRecordListOutputSLZ

    def get_queryset(self) -> QuerySet[TenantSyncTask]:
        cur_tenant_id = self.get_current_tenant_id()
        return TenantSyncTask.objects.filter(tenant_id=cur_tenant_id).exclude(
            data_source__owner_tenant_id=cur_tenant_id
        )

    def get_serializer_context(self) -> Dict[str, Any]:
        return {"tenant_name_map": {t.id: t.name for t in Tenant.objects.all()}}

    @swagger_auto_schema(
        tags=["collaborative"],
        operation_description="协同策略同步记录列表",
        responses={status.HTTP_200_OK: CollaborativeSyncRecordListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
