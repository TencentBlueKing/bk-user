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
from typing import Dict, List
from uuid import UUID

from bkuser_core.audit.models import AuditObjMetaInfo
from bkuser_core.categories.constants import CategoryStatus, CategoryType, SyncStep, SyncTaskStatus
from bkuser_core.categories.db_managers import ProfileCategoryManager
from bkuser_core.common.models import TimestampedModel
from bkuser_core.departments.models import Department
from bkuser_core.profiles.constants import ProfileStatus
from bkuser_core.profiles.models import Profile
from bkuser_core.user_settings.models import Setting, SettingMeta
from django.db import models
from django.utils import timezone
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

    def delete(self, using=None, keep_parents=False):
        """保护默认用户目录不被删除"""
        if self.default:
            raise ValueError("default category can not be deleted.")

        # 手动禁用相关资源，同时保留关联关系
        Profile.objects.disable(
            category_id=self.id,
            disable_param={"enabled": False, "status": ProfileStatus.DELETED.value},
        )
        Department.objects.disable(category_id=self.id)
        Setting.objects.disable(category_id=self.id)

        # 删除周期任务
        try:
            PeriodicTask.objects.get(name=str(self.id)).delete()
        except PeriodicTask.DoesNotExist:
            pass

        self.enabled = False
        self.status = CategoryStatus.INACTIVE.value
        self.save()

    @property
    def configured(self) -> bool:
        """是否配置就绪"""
        # 存在任何必要的配置没有被满足，即配置未就绪
        return not bool(self.get_unfilled_settings())

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

    def make_default_settings(self):
        """创建默认配置"""
        metas = SettingMeta.objects.filter(category_type=self.type)
        for meta in metas:
            Setting.objects.get_or_create(category_id=self.id, meta=meta, value=meta.default)
        return

    def to_audit_info(self):
        """提供审计元信息"""
        return AuditObjMetaInfo(key=self.domain, display_name=self.display_name, category_id=self.id)


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
    task_id = models.UUIDField(db_index=True, verbose_name="任务id")
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
