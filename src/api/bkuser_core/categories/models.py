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
import datetime
from typing import Dict, List
from uuid import UUID, uuid4

from bkuser_core.audit.models import AuditObjMetaInfo
from bkuser_core.categories.constants import (
    TIMEOUT_THRESHOLD,
    CategoryStatus,
    CategoryType,
    SyncStep,
    SyncTaskStatus,
    SyncTaskType,
)
from bkuser_core.categories.db_managers import ProfileCategoryManager
from bkuser_core.categories.exceptions import ExistsSyncingTaskError
from bkuser_core.common.models import TimestampedModel
from bkuser_core.departments.models import Department
from bkuser_core.profiles.constants import ProfileStatus
from bkuser_core.profiles.models import Profile
from bkuser_core.user_settings.models import Setting, SettingMeta
from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django_celery_beat.models import PeriodicTask


class ProfileCategory(TimestampedModel):
    """用户目录"""

    type = models.CharField(verbose_name="类型", max_length=32, choices=CategoryType.get_choices())
    description = models.TextField("描述文字", null=True, blank=True)
    display_name = models.CharField(verbose_name="展示名称", max_length=64)
    domain = models.CharField(verbose_name="登陆域", max_length=64, db_index=True, unique=True)
    default = models.BooleanField(verbose_name="默认目录", default=False)
    enabled = models.BooleanField(default=True)
    status = models.CharField(
        verbose_name="目录状态",
        choices=CategoryStatus.get_choices(),
        default=CategoryStatus.NORMAL.value,
        max_length=32,
    )
    # TODO： order 相关内容其实是 SaaS 强相关，是否考虑挪到 SaaS 中完成
    order = models.IntegerField(verbose_name="额外顺序", default=0)
    last_synced_time = models.DateTimeField("最新同步时间", null=True, blank=True)

    objects = ProfileCategoryManager()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Category-{self.id}-{self.domain}"

    @property
    def inactive(self) -> bool:
        return self.status == CategoryStatus.INACTIVE.value

    def enable(self):
        Profile.objects.enable_or_disable(
            True, category_id=self.id, enable_param={"enabled": True, "status": ProfileStatus.NORMAL.value}
        )
        Department.objects.enable_or_disable(True, category_id=self.id)
        Setting.objects.enable_or_disable(True, category_id=self.id)
        self.enabled = True
        self.status = CategoryStatus.NORMAL.value
        self.save(update_fields=["enabled", "status", "update_time"])

    def delete(self, using=None, keep_parents=False):
        """保护默认用户目录不被删除"""
        if self.default:
            raise ValueError("default category can not be deleted.")

        # 手动禁用相关资源，同时保留关联关系
        Profile.objects.enable_or_disable(
            False,
            category_id=self.id,
            disable_param={"enabled": False, "status": ProfileStatus.DELETED.value},
        )
        Department.objects.enable_or_disable(False, category_id=self.id)
        Setting.objects.enable_or_disable(False, category_id=self.id)

        # 删除周期任务
        try:
            PeriodicTask.objects.get(name=str(self.id)).delete()
        except PeriodicTask.DoesNotExist:
            pass

        self.enabled = False
        self.status = CategoryStatus.INACTIVE.value
        self.save(update_fields=["enabled", "status", "update_time"])

    @property
    def configured(self) -> bool:
        """是否配置就绪"""
        # 存在任何必要的配置没有被满足，即配置未就绪
        return not bool(self.get_unfilled_settings())

    @property
    def syncing(self) -> bool:
        """是否正在同步"""
        return self.synctask_set.filter(status=SyncTaskStatus.RUNNING.value).exists()

    def get_required_metas(self):
        """获取所有必须的配置"""
        return SettingMeta.objects.get_required_metas(self.type)

    def get_unfilled_settings(self):
        """获取未就绪的配置"""
        required_metas = self.get_required_metas()
        configured_meta_ids = self.settings.filter(enabled=True).values_list("meta", flat=True)
        return required_metas.exclude(id__in=configured_meta_ids)

    def mark_synced(self):
        """标记最近成功同步时间"""
        self.last_synced_time = timezone.now()
        self.save(update_fields=["last_synced_time"])
        return

    def make_default_settings(self) -> List[Setting]:
        """创建默认配置"""
        metas = SettingMeta.objects.filter(category_type=self.type)
        settings_result = []
        for meta in metas:
            instance, _ = Setting.objects.get_or_create(category_id=self.id, meta=meta, value=meta.default)
            settings_result.append(instance)
        return settings_result

    def to_audit_info(self):
        """提供审计元信息"""
        return AuditObjMetaInfo(key=self.domain, display_name=self.display_name, category_id=self.id)


class SyncTaskManager(models.Manager):
    def register_task(
        self, category: ProfileCategory, operator: str, type_: SyncTaskType = SyncTaskType.MANUAL
    ) -> 'SyncTask':
        qs = self.filter(category=category, status=SyncTaskStatus.RUNNING.value).order_by("-create_time")
        running = qs.first()
        if not running:
            instance = self.create(
                category=category, status=SyncTaskStatus.RUNNING.value, type=type_.value, operator=operator
            )
            return instance

        # 防御逻辑, 避免 celery 异常后, 一直无法重试.
        delta = now() - running.create_time
        if delta > TIMEOUT_THRESHOLD:
            qs.update(status=SyncTaskStatus.FAILED.value)
            return self.register_task(category=category, operator=operator, type_=type_)
        raise ExistsSyncingTaskError(
            _("当前目录处于同步状态, 请在 {timeout}s 后重试.").format(timeout=(TIMEOUT_THRESHOLD - delta).total_seconds())
        )


class SyncTask(TimestampedModel):
    id = models.UUIDField('UUID', default=uuid4, primary_key=True, editable=False, auto_created=True, unique=True)
    category = models.ForeignKey(ProfileCategory, verbose_name="用户目录", on_delete=models.CASCADE, db_index=True)
    status = models.CharField(
        verbose_name="状态", max_length=16, choices=SyncTaskStatus.get_choices(), default=SyncTaskStatus.RUNNING.value
    )
    type = models.CharField(
        verbose_name="触发类型", max_length=16, choices=SyncTaskType.get_choices(), default=SyncTaskType.MANUAL.value
    )
    operator = models.CharField(max_length=255, verbose_name="操作人", default="nobody")

    objects = SyncTaskManager()

    @property
    def required_time(self) -> datetime.timedelta:
        return self.update_time - self.create_time

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.status = SyncTaskStatus.FAILED.value
            self.save(update_fields=["status", "update_time"])

    @property
    def progresses(self):
        # 由于建表顺序的原因, SyncProgress 的 task_id 未设置成外键....
        # 所以这里用一个 property 实现逻辑上的外键关联.
        return SyncProgress.objects.filter(task_id=self.id)


class SyncProgressManager(models.Manager):
    def init_progresses(self, category: ProfileCategory, task_id: UUID) -> Dict[SyncStep, 'SyncProgress']:
        progresses: Dict[SyncStep, 'SyncProgress'] = {}
        for step in [
            SyncStep.DEPARTMENTS,
            SyncStep.USERS,
            SyncStep.DEPT_USER_RELATIONSHIP,
            SyncStep.USERS_RELATIONSHIP,
        ]:
            progresses[step], created = self.get_or_create(category=category, step=step.value, task_id=task_id)
            if created:
                SyncProgressLog.objects.create(progress=progresses[step])
        return progresses


class SyncProgress(TimestampedModel):
    task_id = models.UUIDField(db_index=True, verbose_name='任务id')
    category = models.ForeignKey(ProfileCategory, verbose_name="用户目录", on_delete=models.CASCADE)
    step = models.CharField(verbose_name="同步步骤", max_length=32, choices=SyncStep.get_choices())
    status = models.CharField(
        verbose_name="状态", max_length=16, choices=SyncTaskStatus.get_choices(), default=SyncTaskStatus.RUNNING.value
    )
    successful_count = models.IntegerField(verbose_name="同步成功数量", default=0)
    failed_count = models.IntegerField(verbose_name="同步失败数量", default=0)

    objects = SyncProgressManager()

    class Meta:
        unique_together = ("category", "step", "task_id")

    @property
    def logs(self):
        try:
            return self.log.logs
        except SyncProgressLog.DoesNotExist:
            self.logs = ""
        return self.log.logs

    @logs.setter
    def logs(self, logs: str):
        try:
            self.log.logs = logs
            self.log.save(update_fields=["logs", "update_time"])
        except SyncProgressLog.DoesNotExist:
            SyncProgressLog.objects.create(progress=self, logs=logs)

    @property
    def failed_records(self):
        try:
            return self.log.failed_records
        except SyncProgressLog.DoesNotExist:
            self.failed_records = []
        return self.log.failed_records

    @failed_records.setter
    def failed_records(self, failed_records: List):
        try:
            self.log.failed_records = failed_records
            self.log.save(update_fields=["failed_records"])
        except SyncProgressLog.DoesNotExist:
            SyncProgressLog.objects.create(progress=self, failed_records=failed_records)


class SyncProgressLog(TimestampedModel):
    progress = models.OneToOneField(SyncProgress, on_delete=models.CASCADE, related_name="log")
    logs = models.TextField(verbose_name="日志")
    failed_records = models.JSONField(default=list)
