# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from typing import List

from blue_krill.models.fields import EncryptField
from django.conf import settings
from django.db import models, transaction

from bkuser.common.constants import SENSITIVE_MASK
from bkuser.common.models import AuditedModel, TimestampedModel
from bkuser.idp_plugins.base import BasePluginConfig, get_plugin_cfg_cls, get_plugin_type
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum, PluginTypeEnum
from bkuser.utils import dictx
from bkuser.utils.url import urljoin
from bkuser.utils.uuid import generate_uuid

from .constants import IdpStatus
from .data_models import DataSourceMatchRule, DataSourceMatchRuleList


class IdpPlugin(models.Model):
    """认证源插件"""

    id = models.CharField("认证源插件唯一标识", primary_key=True, max_length=128)
    name = models.CharField("认证源插件名称", max_length=128, unique=True)
    description = models.TextField("描述", default="", blank=True)
    logo = models.TextField("Logo", null=True, blank=True, default="")


class IdpQuerySet(models.QuerySet):
    """认证源 QuerySet 类"""

    @transaction.atomic()
    def create(self, **kwargs):
        if "plugin_config" not in kwargs:
            return super().create(**kwargs)

        plugin_cfg = kwargs.pop("plugin_config")
        assert isinstance(plugin_cfg, BasePluginConfig)

        idp: Idp = super().create(**kwargs)
        idp.set_plugin_cfg(plugin_cfg)
        return idp


# 认证源管理器类
IdpManager = models.Manager.from_queryset(IdpQuerySet)


class Idp(AuditedModel):
    """认证源"""

    # 登录回调场景下，该 ID 是 URL Path 的一部分
    id = models.CharField("认证源标识", primary_key=True, max_length=128, default=generate_uuid)
    name = models.CharField("认证源名称", max_length=128)
    owner_tenant_id = models.CharField("归属租户", max_length=64, db_index=True)
    status = models.CharField("认证源状态", max_length=32, choices=IdpStatus.get_choices(), default=IdpStatus.ENABLED)
    # Note: 认证源插件被删除的前提是，插件没有被任何认证源使用
    plugin = models.ForeignKey(IdpPlugin, on_delete=models.PROTECT)
    plugin_config = models.JSONField("插件配置", default=dict)
    # 认证源与数据源的匹配规则
    data_source_match_rules = models.JSONField("匹配规则", default=list)
    # 冗余字段，用于添加、删除或变更时使用
    # Note: -1 表示无限制，0 表示 "实名数据源"被删除，但不删除认证源，其他 >=0 则表示实际绑定的数据源 ID
    data_source_id = models.IntegerField("数据源 ID")

    objects = IdpManager()

    class Meta:
        ordering = ["created_at"]
        unique_together = [
            ("name", "owner_tenant_id"),
            # 同一个数据源对于同一种类型的认证源插件，只允许配置一个
            ("data_source_id", "plugin", "owner_tenant_id"),
        ]

    @property
    def is_local(self) -> bool:
        """检查类型是否为本地账密认证源"""
        return self.plugin.id == BuiltinIdpPluginEnum.LOCAL

    @property
    def data_source_match_rule_objs(self) -> List[DataSourceMatchRule]:
        """转换为规则对象列表"""
        return DataSourceMatchRuleList.validate_python(self.data_source_match_rules)

    @property
    def callback_uri(self) -> str:
        plugin_type = get_plugin_type(self.plugin.id)
        # 联邦登录才有回调地址
        if plugin_type == PluginTypeEnum.FEDERATION:
            return urljoin(settings.BK_LOGIN_URL, f"auth/idps/{self.id}/actions/callback/")

        return ""

    def get_plugin_cfg(self) -> BasePluginConfig:
        """获取插件配置

        注意：使用该方法获取到的配置将会包含敏感信息，不适合通过 API 暴露出去，仅可用于内部逻辑流转
        API 要获取插件配置请使用 idp.plugin_config，其中的敏感信息将会被 ******* 取代
        """
        plugin_cfg = self.plugin_config
        for info in IdpSensitiveInfo.objects.filter(idp=self):
            # 嵌套路径中可能某层的值为 None，此时应该跳过
            if not dictx.exist_key(plugin_cfg, info.key):
                continue

            dictx.set_items(plugin_cfg, info.key, info.value)

        PluginCfgCls = get_plugin_cfg_cls(self.plugin.id)  # noqa: N806
        return PluginCfgCls(**plugin_cfg)

    def set_plugin_cfg(self, cfg: BasePluginConfig) -> None:
        """设置插件配置，注意：该方法包含 DB 数据更新，需要在事务中执行"""
        plugin_cfg = cfg.model_dump()

        # 由于单个插件的敏感字段不会很多，这里不采用批量创建/更新的方式
        for field in cfg.sensitive_fields:
            sensitive_val = dictx.get_items(plugin_cfg, field)
            # 若敏感字段无值，或者已经被替换为掩码，则不需要二次替换
            if not sensitive_val or sensitive_val == SENSITIVE_MASK:
                continue

            IdpSensitiveInfo.objects.update_or_create(idp=self, key=field, defaults={"value": sensitive_val})
            dictx.set_items(plugin_cfg, field, SENSITIVE_MASK)

        self.plugin_config = plugin_cfg
        self.save(update_fields=["plugin_config", "updated_at"])


class IdpSensitiveInfo(TimestampedModel):
    """认证源敏感配置信息"""

    idp = models.ForeignKey(Idp, on_delete=models.PROTECT, db_constraint=False)
    key = models.CharField("配置字段路径", max_length=255)
    value = EncryptField(verbose_name="敏感配置数据", max_length=255)

    class Meta:
        unique_together = [("idp", "key")]
