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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Type
from uuid import UUID

import yaml
from rest_framework import serializers
from typing_extensions import Protocol

from bkuser_core.categories.constants import SyncTaskStatus
from bkuser_core.categories.loader import register_plugin
from bkuser_core.categories.models import ProfileCategory, SyncProgress, SyncTask
from bkuser_core.categories.plugins.base import LoginHandler, Syncer
from bkuser_core.categories.plugins.constants import HookType
from bkuser_core.common.models import is_obj_needed_update
from bkuser_core.user_settings.models import Setting, SettingMeta

logger = logging.getLogger(__name__)


class SyncRecordSLZ(serializers.Serializer):
    detail = serializers.DictField(child=serializers.CharField())
    success = serializers.BooleanField()
    dt = serializers.DateTimeField()


class PluginHook(Protocol):
    """插件钩子，用于各种事件后的回调"""

    def trigger(self, status: str, params: dict):
        raise NotImplementedError


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
    settings_path: Optional[Path] = None
    # 其他额外配置
    extra_config: dict = field(default_factory=dict)

    hooks: Dict[HookType, Type[PluginHook]] = field(default_factory=dict)

    def register(self):
        """注册插件"""
        register_plugin(self)
        if self.settings_path is not None:
            self.load_settings_from_yaml()

    def init_settings(self, setting_meta_key: str, meta_info: dict, category_configured_dict: Dict[int, bool]):
        namespace = meta_info.pop("namespace", "general")

        try:
            meta, created = SettingMeta.objects.get_or_create(
                key=setting_meta_key, category_type=self.name, namespace=namespace, defaults=meta_info
            )
            if created:
                logger.debug("\n------ SettingMeta<%s> of plugin<%s> created.", setting_meta_key, self.name)
        except Exception:  # pylint: disable=broad-except
            logger.exception("SettingMeta<%s> of plugin<%s> can not been created.", setting_meta_key, self.name)
            return

        if is_obj_needed_update(meta, meta_info):
            for k, v in meta_info.items():
                setattr(meta, k, v)

            try:
                meta.save()
            except Exception:  # pylint: disable=broad-except
                logger.exception("SettingMeta<%s> of plugin<%s> can not been updated.", setting_meta_key, self.name)
                return
            logger.debug("\n------ SettingMeta<%s> of plugin<%s> updated.", setting_meta_key, self.name)

        # 默认在创建 meta 后创建 settings，保证新增的配置能够被正确初始化
        if meta.default is not None:
            # 理论上目录不能够被直接恢复, 所以已经被删除的目录不会被更新
            # 仅做新增，避免覆盖已有配置
            for category in ProfileCategory.objects.filter(type=self.category_type, enabled=True):
                # if we don't know the category is configured or not, skip it for now
                if category.id not in category_configured_dict:
                    continue

                # if the category is not configured, skip it
                if not category_configured_dict[category.id]:
                    continue

                try:
                    ins, created = Setting.objects.get_or_create(
                        meta=meta, category_id=category.id, defaults={"value": meta.default}
                    )
                    if created:
                        logger.debug("\n------ Setting<%s> of category<%s> created.", ins, category)
                except Exception:  # pylint: disable=broad-except
                    logger.exception(
                        "Setting default of meta<%s>, category_id<%s>, defaults<%s> can not been created.",
                        meta,
                        category.id,
                        meta.default,
                    )
                    continue

    # FIXME: 这类初始化是否不应该放在 registry? (每次程序加载都会执行registry)
    def load_settings_from_yaml(self):
        """从 yaml 中加载 SettingMeta 配置"""
        category_configured_dict = {}
        for category in ProfileCategory.objects.filter(type=self.category_type, enabled=True):
            category_configured_dict[category.id] = category.configured

        with self.settings_path.open(mode="r") as f:
            for key, meta_info in yaml.safe_load(f).items():
                self.init_settings(key, meta_info, category_configured_dict)

    def get_hook(self, type_: HookType) -> Optional[PluginHook]:
        hook_cls = self.hooks.get(type_)
        return hook_cls() if hook_cls else None

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
