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
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.mixins import CurrentUserTenantMixin
from bkuser.apps.global_setting.models import GlobalSetting
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.common.views import ExcludePatchAPIViewMixin

from .serializers import GlobalSettingRetrieveOutputSLZ, GlobalSettingUpdateInputSLZ


class GlobalSettingRetrieveUpdateApi(ExcludePatchAPIViewMixin, CurrentUserTenantMixin, generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.MANAGE_PLATFORM)]

    lookup_url_kwarg = "id"
    queryset = GlobalSetting.objects.all()
    serializer_class = GlobalSettingRetrieveOutputSLZ

    @swagger_auto_schema(
        tags=["global-setting"],
        operation_description="全局配置",
        responses={status.HTTP_200_OK: GlobalSettingRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["global-setting"],
        operation_description="更新全局配置",
        request_body=GlobalSettingUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        instance = self.get_object()

        slz = GlobalSettingUpdateInputSLZ(data=request.data, context={"global_setting_id": instance.id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        instance.value = data["value"]
        instance.save(update_fields=["value", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)
