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
from dataclasses import dataclass, field
from typing import Optional, Type
from uuid import UUID

from bkuser_core.categories.constants import SyncTaskStatus
from bkuser_core.categories.loader import register_plugin
from bkuser_core.categories.models import SyncProgress, SyncTask
from bkuser_core.categories.plugins.base import LoginHandler, Syncer
from rest_framework import serializers


class SyncRecordSLZ(serializers.Serializer):
    detail = serializers.DictField(child=serializers.CharField())
    success = serializers.BooleanField()
    dt = serializers.DateTimeField()


@dataclass
class DataSourcePlugin:
    """数据源插件，定义不同的数据源"""

    name: str
    syncer_cls: Type[Syncer]
    # 绑定的目录类型
    # 后期会将去掉目录类型的概念，只存在租户组和插件之间的直接对应关系
    # 届时，将直接通过插件名获取，同时删除该变量
    # TODO: remove me
    category_type: Optional[str] = ""
    # 额外配置，预留扩展
    # 用于处理登录相关逻辑，目前只支持简单 check 逻辑
    # 是否允许通过 SaaS 修改，默认不允许
    allow_client_write: bool = field(default_factory=lambda: False)
    login_handler_cls: Optional[Type[LoginHandler]] = None
    # 其他额外配置
    extra_config: dict = field(default_factory=dict)

    def register(self):
        """注册插件"""
        register_plugin(self)

    def sync(self, instance_id: int, task_id: UUID, *args, **kwargs):
        """同步数据"""
        syncer = self.syncer_cls(category_id=instance_id)
        category = syncer.category
        task = SyncTask.objects.get(id=task_id)
        progresses = SyncProgress.objects.init_progresses(category, task_id=task_id)
        try:
            syncer.sync(*args, **kwargs)
        finally:
            task_status = SyncTaskStatus.SUCCESSFUL.value
            for item in syncer.context.report():
                if not item.successful:
                    task_status = SyncTaskStatus.FAILED.value
                progress = progresses[item.step]
                fields = {
                    "status": SyncTaskStatus.SUCCESSFUL.value if item.successful else SyncTaskStatus.FAILED.value,
                    "successful_count": len(item.successful_items),
                    "failed_count": len(item.failed_items),
                    "logs": "\n".join(item.logs),
                    "failed_records": SyncRecordSLZ(item.failed_items, many=True).data,
                }
                for key, value in fields.items():
                    setattr(progress, key, value)
                progress.save(update_fields=["status", "successful_count", "failed_count", "update_time"])
            # 更新任务状态
            task.status = task_status
            task.save(update_fields=["status", "update_time"])
