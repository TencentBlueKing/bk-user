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
from rest_framework import generics

from .serializers import SyncTaskInputSLZ, SyncTaskOutputSLZ, SyncTaskProcessOutputSLZ
from bkuser_core.api.web.utils import get_operator
from bkuser_core.api.web.viewset import CustomPagination
from bkuser_core.bkiam.constants import IAMAction
from bkuser_core.bkiam.permissions import Permission
from bkuser_core.categories.models import SyncTask


class SyncTaskListApi(generics.ListAPIView):
    # permission_classes = []
    pagination_class = CustomPagination
    serializer_class = SyncTaskOutputSLZ

    def get_queryset(self):
        operator = get_operator(self.request)
        slz = SyncTaskInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        queryset = SyncTask.objects.all().order_by("-create_time")
        category_id = data.get("category_id")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if settings.ENABLE_IAM:
            fs = Permission().make_filter_of_category(operator, IAMAction.VIEW_CATEGORY)
            queryset = queryset.filter(fs)

        return queryset


class SyncTaskProgressListApi(generics.ListAPIView):
    # permission_classes = []
    serializer_class = SyncTaskProcessOutputSLZ

    lookup_field = "task_id"

    def get_queryset(self):
        task_id = self.kwargs.get("task_id")
        task = SyncTask.objects.get(id=task_id)

        if settings.ENABLE_IAM:
            operator = get_operator(self.request)
            Permission().allow_category_action(operator, IAMAction.VIEW_CATEGORY, task.category)

        return task.progresses.order_by("-create_time")
