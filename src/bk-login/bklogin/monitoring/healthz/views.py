# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from blue_krill.monitoring.probe.base import ProbeSet
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View

from bklogin.common.error_codes import error_codes
from bklogin.common.response import APISuccessResponse

from .probes import get_default_probes


class PingApi(View):
    """就绪&存活探测 API"""

    def get(self, request, *args, **kwargs):
        return HttpResponse("pong")


class HealthzApi(View):
    """健康探测 API"""

    def get(self, request, *args, **kwargs):
        token = request.GET.get("token", "")
        if not settings.HEALTHZ_TOKEN:
            raise error_codes.UNAUTHENTICATED.f(
                "Healthz token was not configured in settings, request denied", replace=True
            )
        if not (token and token == settings.HEALTHZ_TOKEN):
            raise error_codes.UNAUTHENTICATED.f("Please provide valid token", replace=True)

        probe_set = ProbeSet(get_default_probes())
        diagnosis_list = probe_set.examination()

        if diagnosis_list.is_death:
            # if something deadly exist, we have to make response non-200 which is easier to be found
            # by monitor system and make response as a plain text
            raise error_codes.SYSTEM_ERROR.f("internal server error", replace=True).set_data(
                diagnosis_list.get_fatal_report()
            )

        results = [
            {
                "system_name": i.system_name,
                "alive": i.alive,
                "issues": [{"fatal": j.fatal, "description": j.description} for j in i.issues],
            }
            for i in diagnosis_list.items
        ]

        return APISuccessResponse(data={"results": results})
