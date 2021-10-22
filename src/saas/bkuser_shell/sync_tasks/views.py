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
import bkuser_sdk
from bkuser_shell.bkiam.constants import ActionEnum
from bkuser_shell.common.viewset import BkUserApiViewSet
from bkuser_shell.sync_tasks import serializers as slzs

from bkuser_global.drf_crown import inject_serializer


class SyncTaskViewSet(BkUserApiViewSet):
    ACTION_ID = ActionEnum.VIEW_CATEGORY.value

    @inject_serializer(query_in=slzs.SearchSerializer, out=slzs.SyncTaskResponseSerializer, tags=["sync_tasks"])
    def list(self, request, validated_data):
        page = validated_data["page"]
        page_size = validated_data["page_size"]

        api_instance = bkuser_sdk.SyncTaskApi(self.get_api_client_by_request(request))
        response = api_instance.v2_sync_task_list(page=page, page_size=page_size)
        return response

    @inject_serializer(out=slzs.SyncTaskProcessSerializer(many=True), tags=["sync_tasks"])
    def show_logs(self, request, task_id):
        api_instance = bkuser_sdk.SyncTaskApi(self.get_api_client_by_request(request))
        response = api_instance.v2_sync_task_show_logs(task_id)
        return response
