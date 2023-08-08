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
from django.conf import settings
from django_prometheus.exports import ExportToDjangoView
from rest_framework import status
from rest_framework.response import Response


def metric_view(request):
    """metric view with basic auth"""
    token = request.GET.get("token", "")
    if not settings.METRIC_TOKEN:
        return Response(
            data={"errors": "Metric token was not configured in settings, request denied"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not (token and token == settings.METRIC_TOKEN):
        return Response(
            data={"errors": "Please provide valid token"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return ExportToDjangoView(request)
