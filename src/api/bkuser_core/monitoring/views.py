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
from django.http import HttpResponse, JsonResponse
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny

from .base import ProbeSet
from .probes import get_default_probes
from .serializers import DiagnosisSerializer


class HealthViewSet(viewsets.ViewSet):
    permission_classes = [
        AllowAny,
    ]

    def healthz(self, request):
        probe_set = ProbeSet(get_default_probes())
        diagnosis_list = probe_set.examination()

        if diagnosis_list.is_death():
            # if something deadly exist, we have to make response non-200 which is easier to be found
            # by monitor system and make response as a plain text
            return HttpResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=str(diagnosis_list.get_death_report()),
            )

        return JsonResponse(data={"results": DiagnosisSerializer(diagnosis_list.diagnoses, many=True).data})

    def pong(self, request):
        return HttpResponse(content="pong")
