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

from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apis.web.organization.serializers import (
    RequiredTenantUserFieldOutputSLZ,
    TenantListOutputSLZ,
    TenantRetrieveOutputSLZ,
)
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.models import Tenant, TenantDepartment, TenantUser, TenantUserCustomField, UserBuiltinField


class CurrentTenantRetrieveApi(CurrentUserTenantMixin, generics.RetrieveAPIView):
    """获取当前用户所在租户信息"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    @swagger_auto_schema(
        tags=["organization.tenant"],
        operation_description="获取当前用户所在租户信息",
        responses={status.HTTP_200_OK: TenantRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant = Tenant.objects.get(id=self.get_current_tenant_id())
        return Response(TenantRetrieveOutputSLZ(tenant).data, status=status.HTTP_200_OK)


class CollaborativeTenantListApi(CurrentUserTenantMixin, generics.ListAPIView):
    """获取当前租户的协作租户信息"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    pagination_class = None
    serializer_class = TenantListOutputSLZ

    def get_queryset(self):
        # FIXME (su) 目前是根据部门信息获取的协作租户 ID，后续可修改成根据协同策略获取？
        # 不过通过部门反查优点是一定有数据（协作策略已确认，但是未同步的情况）
        cur_tenant_id = self.get_current_tenant_id()
        dept_tenant_ids = (
            TenantDepartment.objects.filter(tenant_id=cur_tenant_id)
            .exclude(data_source__owner_tenant_id=cur_tenant_id)
            .values_list("data_source__owner_tenant_id", flat=True)
            .distinct()
        )
        user_tenant_ids = (
            TenantUser.objects.filter(tenant_id=cur_tenant_id)
            .exclude(data_source__owner_tenant_id=cur_tenant_id)
            .values_list("data_source__owner_tenant_id", flat=True)
            .distinct()
        )
        # 需要用户和部门的 owner_tenant_id 取并集，避免出现用户不属于任何部门的情况
        collaborative_tenant_ids = set(dept_tenant_ids) | set(user_tenant_ids)
        return Tenant.objects.filter(id__in=collaborative_tenant_ids)

    @swagger_auto_schema(
        tags=["organization.tenant"],
        operation_description="获取当前租户的协作租户信息",
        responses={status.HTTP_200_OK: TenantListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RequiredTenantUserFieldListApi(CurrentUserTenantMixin, generics.ListAPIView):
    """租户用户必填字段（快速录入用）"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_TENANT)]

    pagination_class = None

    @swagger_auto_schema(
        tags=["organization.tenant"],
        operation_description="快速录入租户用户必填字段",
        responses={status.HTTP_200_OK: RequiredTenantUserFieldOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        cur_tenant_id = self.get_current_tenant_id()
        # 默认的内置字段，虽然邮箱 & 手机在 DB 中不是必填，但是在
        # 快速录入场景中要求必填，手机国际区号与手机号合并，不需要单独提供
        field_infos = [
            {"name": f.name, "display_name": f.display_name, "tips": ""}
            for f in UserBuiltinField.objects.exclude(name="phone_country_code")
        ]
        for f in TenantUserCustomField.objects.filter(tenant_id=cur_tenant_id, required=True):
            opts = ", ".join(opt["id"] for opt in f.options)

            if f.data_type == UserFieldDataType.ENUM:
                tips = _("单选枚举，可选值：{}").format(opts)
            elif f.data_type == UserFieldDataType.MULTI_ENUM:
                tips = _("多选枚举，多个值以 / 分隔，可选值：{}").format(opts)
            else:
                tips = _("数据类型：{}").format(UserFieldDataType.get_choice_label(f.data_type))

            field_infos.append({"name": f.name, "display_name": f.display_name, "tips": tips})

        return Response(RequiredTenantUserFieldOutputSLZ(field_infos, many=True).data, status=status.HTTP_200_OK)
