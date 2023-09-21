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

from bkuser.apis.web.tenant_setting.serializers import (
    UserCustomFieldCreateInputSLZ,
    UserCustomFieldCreateOutputSLZ,
    UserCustomFieldUpdateInputSLZ,
    UserFieldOutputSLZ,
)
from bkuser.apps.tenant.models import Tenant
from bkuser.apps.tenant_setting.models import UserBuiltinField, UserCustomField
from bkuser.common.error_codes import error_codes
from bkuser.common.views import ExcludePutAPIViewMixin


class UserFieldListApi(generics.ListAPIView):
    pagination_class = None
    serializer_class = UserFieldOutputSLZ

    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="用户字段列表",
        responses={status.HTTP_200_OK: UserFieldOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        # 校验租户是否存在
        tenant = Tenant.objects.filter(id=kwargs["tenant_id"]).first()
        if not tenant:
            raise error_codes.TENANT_NOT_EXIST

        slz = UserFieldOutputSLZ(
            instance={
                "builtin_fields": UserBuiltinField.objects.all().values(),
                "custom_fields": UserCustomField.objects.filter(tenant=tenant).values(),
            }
        )
        return Response(slz.data)


class UserCustomFieldCreateApi(generics.CreateAPIView):
    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="新建用户自定义字段",
        request_body=UserCustomFieldCreateInputSLZ(),
        responses={status.HTTP_201_CREATED: UserCustomFieldCreateOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        # 校验租户是否存在
        tenant = Tenant.objects.filter(id=kwargs["tenant_id"]).first()
        if not tenant:
            raise error_codes.TENANT_NOT_EXIST

        slz = UserCustomFieldCreateInputSLZ(data=request.data, context={"tenant": tenant})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        user_custom_field = UserCustomField.objects.create(tenant=tenant, **data)
        return Response(
            UserCustomFieldCreateOutputSLZ(instance={"id": user_custom_field.id}).data, status=status.HTTP_201_CREATED
        )


class UserCustomFieldUpdateDeleteApi(ExcludePutAPIViewMixin, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = UserCustomField.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="修改用户自定义字段",
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def patch(self, request, *args, **kwargs):
        custom_field = self.get_object()
        slz = UserCustomFieldUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        UserCustomField.objects.filter(id=custom_field.id).update(**slz.data)
        return Response()

    @swagger_auto_schema(
        tags=["tenant-setting"],
        operation_description="删除用户自定义字段",
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
