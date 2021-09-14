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
from bkuser_shell.categories.serializers import DetailCategorySerializer
from bkuser_shell.sync_tasks import constants
from rest_framework import serializers


class SyncTaskSerializer(serializers.Serializer):
    id = serializers.CharField()
    category = DetailCategorySerializer()
    status = serializers.ChoiceField(choices=constants.SyncTaskStatus.get_choices(), help_text="任务执行状态")
    type = serializers.ChoiceField(choices=constants.SyncTaskType.get_choices(), help_text="任务触发类型")
    operator = serializers.CharField(help_text="操作人")
    create_time = serializers.DateTimeField(help_text="开始时间")
    required_time = serializers.CharField(help_text="耗时, 单位秒")


class SyncTaskProcessSerializer(serializers.Serializer):
    step = serializers.ChoiceField(choices=constants.SyncStep.get_choices(), help_text="同步步骤")
    status = serializers.ChoiceField(choices=constants.SyncTaskStatus.get_choices(), help_text="执行状态")
    successful_count = serializers.IntegerField(help_text="同步成功数量")
    failed_count = serializers.IntegerField(help_text="同步失败数量")
    logs = serializers.CharField(help_text="纯文本日志")
    failed_records = serializers.ListField(child=serializers.JSONField(), help_text="失败对象名称")


class SyncTaskResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    results = SyncTaskSerializer(many=True)


class SearchSerializer(serializers.Serializer):
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=10)
