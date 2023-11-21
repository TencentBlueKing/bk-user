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
from typing import List
from urllib.parse import urljoin

from django.conf import settings
from django.db import models

from bkuser.common.models import AuditedModel
from bkuser.idp_plugins.base import get_plugin_type
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum, PluginTypeEnum
from bkuser.utils.uuid import generate_uuid

from .constants import IdpStatus
from .data_models import DataSourceMatchRule, DataSourceMatchRuleList


class IdpPlugin(models.Model):
    """认证源插件"""

    id = models.CharField("认证源插件唯一标识", primary_key=True, max_length=128)
    name = models.CharField("认证源插件名称", max_length=128, unique=True)
    description = models.TextField("描述", default="", blank=True)
    logo = models.TextField("Logo", null=True, blank=True, default="")

    class Meta:
        ordering = ["created_at"]


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
    # 允许关联社会化认证源的租户组织架构范围
    allow_bind_scopes = models.JSONField("允许范围", default=list)

    class Meta:
        ordering = ["created_at"]
        unique_together = [
            ("name", "owner_tenant_id"),
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
