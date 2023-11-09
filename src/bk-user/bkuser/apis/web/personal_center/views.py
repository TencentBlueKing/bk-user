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
from typing import Dict

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.personal_center.serializers import (
    NaturalUserWithTenantUserListOutputSLZ,
    PersonalCenterTenantUserRetrieveOutputSLZ,
    TenantUserEmailUpdateInputSLZ,
    TenantUserPhoneUpdateInputSLZ,
)
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.natural_user import NatureUserHandler
from bkuser.biz.tenant import TenantUserEmailInfo, TenantUserHandler, TenantUserPhoneInfo
from bkuser.common.views import ExcludePutAPIViewMixin


class NaturalUserTenantUserListApi(generics.ListAPIView):
    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="个人中心-关联账户列表",
        responses={status.HTTP_200_OK: NaturalUserWithTenantUserListOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        current_tenant_user_id = request.user.username

        # 获取当前登录的租户用户的自然人:两种情况绑定、未绑定，在函数中做处理
        nature_user = NatureUserHandler.get_nature_user_by_tenant_user_id(current_tenant_user_id)

        tenant_users = TenantUser.objects.select_related("data_source_user").filter(
            data_source_user_id__in=nature_user.data_source_user_ids
        )

        # 将当前登录置顶
        # 通过比对租户用户id, 当等于当前登录用户的租户id，将其排序到查询集的顶部, 否则排序到查询集的底部
        sorted_tenant_users = sorted(tenant_users, key=lambda t: t.id != current_tenant_user_id)

        # 响应数据组装
        nature_user_with_tenant_users_info: Dict = {
            "id": nature_user.id,
            "full_name": nature_user.full_name,
            "tenant_users": [
                {
                    "id": user.id,
                    "username": user.data_source_user.username,
                    "full_name": user.data_source_user.full_name,
                    "tenant": {"id": user.tenant_id, "name": user.tenant.name},
                }
                for user in sorted_tenant_users
            ],
        }

        return Response(NaturalUserWithTenantUserListOutputSLZ(nature_user_with_tenant_users_info).data)


class TenantUserRetrieveApi(generics.RetrieveAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]
    serializer_class = PersonalCenterTenantUserRetrieveOutputSLZ

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="个人中心-关联账户详情",
        responses={status.HTTP_200_OK: PersonalCenterTenantUserRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return Response(PersonalCenterTenantUserRetrieveOutputSLZ(self.get_object()).data)


class TenantUserPhoneUpdateApi(ExcludePutAPIViewMixin, generics.UpdateAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="租户用户更新手机号",
        request_body=TenantUserPhoneUpdateInputSLZ,
        responses={status.HTTP_200_OK: ""},
    )
    def patch(self, request, *args, **kwargs):
        slz = TenantUserPhoneUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        phone_info = TenantUserPhoneInfo(
            is_inherited_phone=data["is_inherited_phone"],
            custom_phone=data.get("custom_phone", ""),
            custom_phone_country_code=data["custom_phone_country_code"],
        )
        TenantUserHandler.update_tenant_user_phone(self.get_object(), phone_info)
        return Response()


class TenantUserEmailUpdateApi(ExcludePutAPIViewMixin, generics.UpdateAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="租户用户更新手机号",
        request_body=TenantUserEmailUpdateInputSLZ,
        responses={status.HTTP_200_OK: ""},
    )
    def patch(self, request, *args, **kwargs):
        slz = TenantUserEmailUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        email_info = TenantUserEmailInfo(
            is_inherited_email=data["is_inherited_email"],
            custom_email=data.get("custom_email", ""),
        )
        TenantUserHandler.update_tenant_user_email(self.get_object(), email_info)
        return Response()
