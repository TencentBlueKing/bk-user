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
from collections import defaultdict
from typing import Dict, List

from django.db import transaction
from django.db.models import Q, QuerySet
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.models import TenantUser, VirtualUserAppRelation, VirtualUserOwnerRelation
from bkuser.apps.tenant.utils import TenantUserIDGenerator
from bkuser.biz.auditor import VirtualUserAuditor
from bkuser.common.views import ExcludePatchAPIViewMixin

from .mixins import CurrentTenantVirtualDataSource
from .serializers import (
    VirtualUserCreateInputSLZ,
    VirtualUserCreateOutputSLZ,
    VirtualUserListInputSLZ,
    VirtualUserListOutputSLZ,
    VirtualUserRetrieveOutputSLZ,
    VirtualUserUpdateInputSLZ,
)


class VirtualUserListCreateApi(CurrentTenantVirtualDataSource, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    serializer_class = VirtualUserListOutputSLZ

    def get_queryset(self) -> QuerySet[TenantUser]:
        slz = VirtualUserListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 过滤当前租户的虚拟用户
        queryset = TenantUser.objects.filter(
            tenant_id=self.get_current_tenant_id(), data_source__type=DataSourceTypeEnum.VIRTUAL
        ).select_related("data_source_user")

        # 关键字过滤
        if keyword := data.get("keyword"):
            queryset = queryset.filter(
                Q(data_source_user__username__icontains=keyword) | Q(data_source_user__full_name__icontains=keyword)
            )
        return queryset

    def get_serializer_context(self):
        queryset = self.paginate_queryset(self.get_queryset())
        if queryset is None:
            return {"app_code_map": {}, "owner_map": {}}
        virtual_user_ids = [user.id for user in queryset]

        app_relations = VirtualUserAppRelation.objects.filter(tenant_user_id__in=virtual_user_ids).values_list(
            "tenant_user_id", "app_code"
        )
        # 虚拟用户与 app_code 之间的映射
        app_code_map: Dict[str, List[str]] = defaultdict(list)
        for tenant_user_id, app_code in app_relations:
            app_code_map[tenant_user_id].append(app_code)

        owner_relations = VirtualUserOwnerRelation.objects.filter(tenant_user_id__in=virtual_user_ids).values_list(
            "tenant_user_id", "owner_id"
        )
        # 虚拟用户与责任人列表之间的映射
        owner_map: Dict[str, List[str]] = defaultdict(list)
        for tenant_user_id, owner_id in owner_relations:
            owner_map[tenant_user_id].append(owner_id)

        return {"app_code_map": app_code_map, "owner_map": owner_map}

    @swagger_auto_schema(
        tags=["virtual_user"],
        operation_description="虚拟用户列表",
        query_serializer=VirtualUserListInputSLZ(),
        responses={status.HTTP_200_OK: VirtualUserListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["virtual_user"],
        operation_description="新建虚拟用户",
        request_body=VirtualUserCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: VirtualUserCreateOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        data_source = self.get_current_virtual_data_source()
        slz = VirtualUserCreateInputSLZ(data=request.data, context={"data_source_id": data_source.id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        with transaction.atomic():
            # 创建数据源用户
            user = DataSourceUser.objects.create(
                data_source=data_source,
                code=data["username"],
                username=data["username"],
                full_name=data["full_name"],
            )
            # 虚拟用户只会同步到数据源所属租户下
            tenant_id = data_source.owner_tenant_id
            tenant_user = TenantUser.objects.create(
                id=TenantUserIDGenerator(tenant_id, data_source).gen(user),
                data_source_user=user,
                tenant_id=tenant_id,
                data_source=data_source,
            )
            # 创建虚拟用户与应用的关联
            VirtualUserAppRelation.objects.bulk_create(
                [
                    VirtualUserAppRelation(
                        tenant_user=tenant_user,
                        app_code=app_code,
                    )
                    for app_code in data["app_codes"]
                ]
            )
            # 创建虚拟用户与责任人的关联
            VirtualUserOwnerRelation.objects.bulk_create(
                [
                    VirtualUserOwnerRelation(
                        tenant_user=tenant_user,
                        owner_id=owner,
                    )
                    for owner in data["owners"]
                ]
            )

        # 【审计】创建虚拟用户审计对象
        auditor = VirtualUserAuditor(request.user.username, self.get_current_tenant_id())
        # 【审计】将审计记录保存至数据库
        auditor.record_create(tenant_user)

        return Response(status=status.HTTP_201_CREATED, data=VirtualUserCreateOutputSLZ(tenant_user).data)


class VirtualUserRetrieveUpdateDestroyApi(
    CurrentTenantVirtualDataSource, ExcludePatchAPIViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    lookup_url_kwarg = "id"
    serializer_class = VirtualUserRetrieveOutputSLZ

    def get_queryset(self) -> QuerySet[TenantUser]:
        # 过滤当前租户的虚拟用户
        return TenantUser.objects.filter(
            tenant_id=self.get_current_tenant_id(), data_source__type=DataSourceTypeEnum.VIRTUAL
        )

    @swagger_auto_schema(
        tags=["virtual_user"],
        operation_description="虚拟用户详情",
        responses={status.HTTP_200_OK: VirtualUserRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["virtual_user"],
        operation_description="更新虚拟用户",
        request_body=VirtualUserUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        slz = VirtualUserUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 计算 app_code 变更
        current_app_codes = set(
            VirtualUserAppRelation.objects.filter(tenant_user=tenant_user).values_list("app_code", flat=True)
        )
        new_app_codes = set(data["app_codes"])
        app_codes_to_delete = current_app_codes - new_app_codes
        app_codes_to_create = new_app_codes - current_app_codes
        # 计算责任人变更
        current_owners = set(
            VirtualUserOwnerRelation.objects.filter(tenant_user=tenant_user).values_list("owner", flat=True)
        )
        new_owners = set(data["owners"])
        owners_to_delete = current_owners - new_owners
        owners_to_create = new_owners - current_owners

        # 【审计】创建虚拟用户审计对象并记录变更前的数据
        auditor = VirtualUserAuditor(request.user.username, self.get_current_tenant_id())
        auditor.pre_record_data_before(tenant_user)

        data_source_user = tenant_user.data_source_user

        with transaction.atomic():
            # 覆盖更新
            data_source_user.full_name = data["full_name"]
            data_source_user.save(update_fields=["full_name", "updated_at"])

            # 更新虚拟用户与应用的关联
            # 需要删除的关系
            if app_codes_to_delete:
                VirtualUserAppRelation.objects.filter(
                    tenant_user=tenant_user, app_code__in=app_codes_to_delete
                ).delete()
            # 需要新增的关系
            if app_codes_to_create:
                VirtualUserAppRelation.objects.bulk_create(
                    [
                        VirtualUserAppRelation(
                            tenant_user=tenant_user,
                            app_code=app_code,
                        )
                        for app_code in app_codes_to_create
                    ]
                )

            # 更新虚拟用户与责任人的关联
            # 需要删除的关系
            if owners_to_delete:
                VirtualUserOwnerRelation.objects.filter(
                    tenant_user=tenant_user, owner_id__in=owners_to_delete
                ).delete()
            # 需要新增的关系
            if owners_to_create:
                VirtualUserOwnerRelation.objects.bulk_create(
                    [
                        VirtualUserOwnerRelation(
                            tenant_user=tenant_user,
                            owner_id=owner,
                        )
                        for owner in owners_to_create
                    ]
                )

        # 【审计】将审计记录保存至数据库
        auditor.record_update(tenant_user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["virtual_user"],
        operation_description="删除虚拟用户",
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        data_source_user = tenant_user.data_source_user

        # 【审计】创建虚拟用户审计对象并记录变更前的数据
        auditor = VirtualUserAuditor(request.user.username, self.get_current_tenant_id())
        auditor.pre_record_data_before(tenant_user)

        with transaction.atomic():
            tenant_user.delete()
            data_source_user.delete()

            # 删除虚拟用户与应用的关联
            VirtualUserAppRelation.objects.filter(tenant_user=tenant_user).delete()
            # 删除虚拟用户和责任人的关联
            VirtualUserOwnerRelation.objects.filter(tenant_user=tenant_user).delete()

        # 【审计】将审计记录保存至数据库
        auditor.record_delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
