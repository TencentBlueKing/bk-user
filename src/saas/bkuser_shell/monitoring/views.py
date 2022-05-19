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

from django.http import HttpResponse
from rest_framework import status

from bkuser_sdk.rest import ApiException
from bkuser_shell.apis.viewset import BkUserApiViewSet
from bkuser_shell.common.response import Response

logger = logging.getLogger(__name__)


class HealthzViewSet(BkUserApiViewSet):
    permission_classes: list = []

    def list(self, request):
        try:
            return self.call_through_api(request)
        except ApiException as e:
            resp = Response(
                data=e.body,
                status=e.status,
                headers=e.headers,
            )
            return resp
        except Exception as e:
            return HttpResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=str(e),
            )

    def pong(self, request):
        return HttpResponse(content="pong")
