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
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apis.web.person_center.serializers import (
    NaturalUserWithTenantUserListOutputSLZ,
    TenantUserEmailUpdateInputSLZ,
    TenantUserPhoneUpdateInputSLZ,
    TenantUserRetrieveOutputSLZ,
)
from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.natural_user import NaturalUserWithTenantUsers, NatureUserHandler, TenantBaseInfo, TenantUserBaseInfo
from bkuser.biz.tenant import TenantUserHandler, TenantUserUpdateEmailInfo, TenantUserUpdatePhoneInfo
from bkuser.common.error_codes import error_codes


class NaturalUserTenantUserListApi(CurrentUserTenantMixin, generics.ListAPIView):
    pagination_class = None

    @swagger_auto_schema(
        tags=["person_center"],
        operation_description="个人中心-关联账户列表",
        responses={status.HTTP_200_OK: NaturalUserWithTenantUserListOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        current_tenant_user_id = self.get_current_tenant_user_id()

        # 获取当前登录的租户用户的自然人:两种情况绑定、未绑定，在函数中做处理
        nature_user = NatureUserHandler.get_nature_user_by_tenant_user_id(current_tenant_user_id)

        # 将当前登录置顶
        # 通过比对租户用户id, 当等于当前登录用户的租户id，将其排序到查询集的顶部, 否则排序到查询集的底部
        tenant_users = TenantUser.objects.select_related("data_source_user").filter(
            data_source_user_id__in=nature_user.data_source_user_ids
        )

        # FIXME:这里后续数据量可能会很大，需要更优的处理方式 / 或者接口增加一个返回字段is_login 做当前登录用户的标识
        sorted_tenant_users = sorted(tenant_users, key=lambda t: t.id != current_tenant_user_id)

        # 响应数据组装
        nature_user_with_tenant_users = NaturalUserWithTenantUsers(
            id=nature_user.id,
            full_name=nature_user.full_name,
            tenant_users=[
                TenantUserBaseInfo(
                    id=user.id,
                    username=user.data_source_user.username,
                    full_name=user.data_source_user.full_name,
                    tenant=TenantBaseInfo(id=user.tenant_id, name=user.tenant.name),
                )
                for user in sorted_tenant_users
            ],
        )

        return Response(NaturalUserWithTenantUserListOutputSLZ(nature_user_with_tenant_users).data)


class TenantUserRetrieveApi(CurrentUserTenantMixin, generics.RetrieveAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    serializer_class = TenantUserRetrieveOutputSLZ

    @swagger_auto_schema(
        tags=["person_center"],
        operation_description="个人中心-关联账户详情",
        responses={status.HTTP_200_OK: TenantUserRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        instance: TenantUser = self.get_object()

        # 获取当前登录的租户用户的自然人
        current_tenant_user_id = self.get_current_tenant_user_id()
        nature_user = NatureUserHandler.get_nature_user_by_tenant_user_id(current_tenant_user_id)

        # 边界限制
        # 该租户用户的数据源用户，不属于当前自然人
        if instance.data_source_user_id not in nature_user.data_source_user_ids:
            raise error_codes.NO_PERMISSION

        return Response(TenantUserRetrieveOutputSLZ(instance).data)


class TenantUserPhonePatchApi(CurrentUserTenantMixin, generics.UpdateAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["person_center"],
        operation_description="租户用户更新手机号",
        request_body=TenantUserPhoneUpdateInputSLZ,
        responses={status.HTTP_200_OK: ""},
    )
    def patch(self, request, *args, **kwargs):
        instance: TenantUser = self.get_object()

        # 获取当前登录的租户用户的自然人
        current_tenant_user_id = self.get_current_tenant_user_id()
        nature_user = NatureUserHandler.get_nature_user_by_tenant_user_id(current_tenant_user_id)

        # 边界限制
        # 该租户用户的数据源用户，不属于当前自然人
        if instance.data_source_user_id not in nature_user.data_source_user_ids:
            raise error_codes.NO_PERMISSION

        input_slz = TenantUserPhoneUpdateInputSLZ(data=request.data)
        input_slz.is_valid(raise_exception=True)

        phone_info = TenantUserUpdatePhoneInfo(**input_slz.validated_data)
        TenantUserHandler.update_tenant_user_phone(instance, phone_info)

        return Response()


class TenantUserEmailPatchApi(CurrentUserTenantMixin, generics.UpdateAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["person_center"],
        operation_description="租户用户更新手机号",
        request_body=TenantUserEmailUpdateInputSLZ,
        responses={status.HTTP_200_OK: ""},
    )
    def patch(self, request, *args, **kwargs):
        instance: TenantUser = self.get_object()

        # 获取当前登录的租户用户的自然人
        current_tenant_user_id = self.get_current_tenant_user_id()
        nature_user = NatureUserHandler.get_nature_user_by_tenant_user_id(current_tenant_user_id)

        # 边界限制
        # 该租户用户的数据源用户，不属于当前自然人下的
        if instance.data_source_user_id not in nature_user.data_source_user_ids:
            raise error_codes.NO_PERMISSION

        input_slz = TenantUserEmailUpdateInputSLZ(data=request.data)
        input_slz.is_valid(raise_exception=True)

        email_info = TenantUserUpdateEmailInfo(**input_slz.validated_data)
        TenantUserHandler.update_tenant_user_email(instance, email_info)

        return Response()