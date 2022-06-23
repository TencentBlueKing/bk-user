import jsonfield
from django.db import models

from bkuser_core.audit.models import AuditObjMetaInfo
from bkuser_core.common.models import TimestampedModel
from bkuser_core.global_settings.constants import GlobalSettingsEnableNamespaces


class GlobalSettingsMeta(TimestampedModel):
    key = models.CharField("全局配置键", max_length=64)
    enabled = models.BooleanField(default=True)
    required = models.BooleanField("是否必要", default=True)
    namespace = models.CharField(
        "命名空间",
        max_length=32,
        db_index=True,
        choices=GlobalSettingsEnableNamespaces.get_choices(),
        default=GlobalSettingsEnableNamespaces.GENERAL.value,
    )

    example = jsonfield.JSONField("示例", default="")
    default = jsonfield.JSONField("默认值", default=None)
    choices = jsonfield.JSONField("可选值", default=[])

    # 对配置项的更细分
    region = models.CharField("领域", max_length=32, default="default")

    class Meta:
        verbose_name = "全局配置元信息表"
        verbose_name_plural = "全局配置元信息表"
        unique_together = ("key", "namespace")
        ordering = ["-create_time"]


class GlobalSettings(TimestampedModel):
    """配置项"""

    value = jsonfield.JSONField("全局配置内容", default={})
    enabled = models.BooleanField(default=True)
    meta = models.ForeignKey(GlobalSettingsMeta, related_name="instances", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "全局配置表"
        verbose_name_plural = "全局配置表"
        ordering = ["-create_time"]
        unique_together = ["meta"]

    def __str__(self):
        return f"{self.meta.namespace}-{self.meta.region}-{self.meta.key}"

    def to_audit_info(self):
        """提供审计元信息"""
        return AuditObjMetaInfo(
            key=self.meta.key,
            display_name=f"{self.meta.key}",
        )
