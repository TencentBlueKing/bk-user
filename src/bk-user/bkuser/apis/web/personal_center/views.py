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

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.personal_center.serializers import (
    NaturalUserWithTenantUserListOutputSLZ,
    TenantUserEmailUpdateInputSLZ,
    TenantUserExtrasUpdateInputSLZ,
    TenantUserFieldOutputSLZ,
    TenantUserLogoUpdateInputSLZ,
    TenantUserPasswordModifyInputSLZ,
    TenantUserPhoneUpdateInputSLZ,
    TenantUserRetrieveOutputSLZ,
)
from bkuser.apps.data_source.models import DataSourceUserDeprecatedPasswordRecord, LocalDataSourceIdentityInfo
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.models import TenantUser, TenantUserCustomField, UserBuiltinField
from bkuser.biz.natural_user import NatureUserHandler
from bkuser.biz.tenant import TenantUserEmailInfo, TenantUserHandler, TenantUserPhoneInfo
from bkuser.common.error_codes import error_codes
from bkuser.common.hashers import check_password, make_password
from bkuser.common.views import ExcludePatchAPIViewMixin


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
                    "logo": user.data_source_user.logo,
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

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="个人中心-关联账户详情",
        responses={status.HTTP_200_OK: TenantUserRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant_user = self.get_object()

        visible_custom_field_names = TenantUserCustomField.objects.filter(
            tenant=tenant_user.tenant, personal_center_visible=True
        ).values_list("name", flat=True)

        slz = TenantUserRetrieveOutputSLZ(
            tenant_user, context={"visible_custom_field_names": visible_custom_field_names}
        )
        return Response(slz.data)


class TenantUserLogoUpdateApi(ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="租户用户更新头像",
        request_body=TenantUserLogoUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = TenantUserLogoUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        tenant_user = self.get_object()
        data_source_user = tenant_user.data_source_user
        data_source_user.logo = data["logo"]
        data_source_user.save(update_fields=["logo", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserPhoneUpdateApi(ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="租户用户更新手机号",
        request_body=TenantUserPhoneUpdateInputSLZ,
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = TenantUserPhoneUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        phone_info = TenantUserPhoneInfo(
            is_inherited_phone=data["is_inherited_phone"],
            custom_phone=data.get("custom_phone", ""),
            custom_phone_country_code=data["custom_phone_country_code"],
        )
        TenantUserHandler.update_tenant_user_phone(self.get_object(), phone_info)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserEmailUpdateApi(ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="租户用户更新手机号",
        request_body=TenantUserEmailUpdateInputSLZ,
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = TenantUserEmailUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        email_info = TenantUserEmailInfo(
            is_inherited_email=data["is_inherited_email"],
            custom_email=data.get("custom_email", ""),
        )
        TenantUserHandler.update_tenant_user_email(self.get_object(), email_info)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserExtrasUpdateApi(ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="租户用户更新自定义字段",
        request_body=TenantUserExtrasUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        data_source_user = tenant_user.data_source_user

        slz = TenantUserExtrasUpdateInputSLZ(
            data=request.data,
            context={
                "tenant_id": tenant_user.tenant_id,
                "data_source_id": data_source_user.data_source_id,
                "data_source_user_id": data_source_user.id,
            },
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source_user.extras.update(data["extras"])
        data_source_user.save(update_fields=["extras", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserFieldListApi(generics.ListAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="个人中心-用户可见字段列表",
        responses={status.HTTP_200_OK: TenantUserFieldOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant_user = self.get_object()

        custom_fields = TenantUserCustomField.objects.filter(tenant=tenant_user.tenant, personal_center_visible=True)
        for f in custom_fields:
            if f.personal_center_editable:
                continue

            selected = tenant_user.data_source_user.extras.get(f.name)
            # 如果该字段是不可编辑的，且是枚举类型，则仅仅返回需要的 options 用于前端展示，避免泄露枚举选项
            if f.data_type == UserFieldDataType.ENUM:
                f.options = [opt for opt in f.options if opt["id"] == selected]
            elif f.data_type == UserFieldDataType.MULTI_ENUM:
                f.options = [opt for opt in f.options if opt["id"] in selected]

        slz = TenantUserFieldOutputSLZ(
            {"builtin_fields": UserBuiltinField.objects.all(), "custom_fields": custom_fields}
        )
        return Response(slz.data)


class TenantUserPasswordModifyApi(ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="租户用户重置密码",
        request_body=TenantUserPasswordModifyInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        data_source_user = tenant_user.data_source_user
        data_source = data_source_user.data_source
        plugin_config = data_source.get_plugin_cfg()

        if not (data_source.is_local and plugin_config.enable_account_password_login):
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(
                _("仅可以重置 已经启用账密登录功能 的 本地数据源 的用户密码")
            )

        slz = TenantUserPasswordModifyInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        old_password = data["old_password"]
        new_password = data["new_password"]

        identify_info = LocalDataSourceIdentityInfo.objects.get(user=data_source_user)
        if not check_password(old_password, identify_info.password):
            raise error_codes.USERNAME_OR_PASSWORD_WRONG_ERROR

        with transaction.atomic():
            identify_info.password = make_password(new_password)
            identify_info.password_updated_at = timezone.now()
            identify_info.save(update_fields=["password", "password_updated_at", "updated_at"])

            DataSourceUserDeprecatedPasswordRecord.objects.create(
                user=data_source_user,
                password=old_password,
                operator=request.user.username,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
