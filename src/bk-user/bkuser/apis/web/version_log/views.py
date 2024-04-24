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

from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class

from .file_extractor import list_version_log
from .serializers import VersionLogListOutputSLZ


class VersionLogListApi(generics.ListAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

    pagination_class = None

    @swagger_auto_schema(
        tags=["version_log"],
        operation_description="版本日志列表",
        responses={status.HTTP_200_OK: VersionLogListOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        data = list_version_log()
        return Response(VersionLogListOutputSLZ(data, many=True).data)
