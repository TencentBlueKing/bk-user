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
import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from bkuser_shell.apis.viewset import BkUserApiViewSet
from bkuser_shell.common.error_codes import error_codes
from bkuser_shell.common.response import Response
from bkuser_shell.version_log.models import VersionLog, VersionLogSet
from bkuser_shell.version_log.utils import get_version_list

logger = logging.getLogger(__name__)


class VersionLogViewSet(BkUserApiViewSet):
    permission_classes: list = []

    @swagger_auto_schema(responses={status.HTTP_200_OK: VersionLogSet}, tags=["version_log"])
    def list(self, request):
        try:
            version_list = get_version_list()
            return Response(data=version_list.dict())
        except ValueError:
            logger.exception("failed to parse release yaml")
            raise error_codes.VERSION_FORMAT_ERROR

    @swagger_auto_schema(responses={status.HTTP_200_OK: VersionLog}, tags=["version_log"])
    def retrieve(self, request, version_number):
        try:
            version_list = get_version_list()
            return Response(data=version_list.get_by_version(version_number).dict())
        except ValueError:
            logger.exception("failed to parse release yaml")
            raise error_codes.VERSION_FORMAT_ERROR
