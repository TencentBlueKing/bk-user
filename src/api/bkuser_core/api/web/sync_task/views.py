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
from rest_framework.generics import ListAPIView

from .serializers import SyncTaskProcessSerializer, SyncTaskSerializer
from bkuser_core.api.web.viewset import CustomPagination
from bkuser_core.bkiam.constants import IAMAction
from bkuser_core.bkiam.permissions import Permission
from bkuser_core.categories.models import SyncTask


class SyncTaskListApi(ListAPIView):
    # permission_classes = []
    pagination_class = CustomPagination
    serializer_class = SyncTaskSerializer

    def get_queryset(self):
        # TODO: change to use self.request.header to get username
        # username = "admin"
        username = self.request.query_params.get('username') or "admin"

        queryset = SyncTask.objects.all().order_by("-create_time")
        if settings.ENABLE_IAM:
            fs = Permission().make_filter_of_category(username, IAMAction.VIEW_CATEGORY)
            queryset = queryset.filter(fs)

        return queryset


class SyncTaskProgressListApi(ListAPIView):
    # permission_classes = []
    pagination_class = CustomPagination
    serializer_class = SyncTaskProcessSerializer

    def get_queryset(self):
        task_id = self.kwargs.get("task_id")
        task = SyncTask.objects.get(id=task_id)

        # TODO: change to use self.request.header to get username
        # username = "admin"
        username = self.request.query_params.get('username') or "admin"
        Permission().allow_category_action(username, IAMAction.VIEW_CATEGORY, task.category)

        return task.progresses.order_by("-create_time")
