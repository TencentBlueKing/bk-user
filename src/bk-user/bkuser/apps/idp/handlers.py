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
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from bkuser.apps.data_source.constants import DataSourceStatus
from bkuser.apps.data_source.models import DataSource
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.idp_plugins.local.plugin import LocalIdpPluginConfig
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

from .constants import IdpStatus
from .data_models import DataSourceMatchRuleList, gen_data_source_match_rule_of_local
from .models import Idp, IdpPlugin


@receiver(post_save, sender=DataSource)
def update_local_idp_of_tenant(sender, instance: DataSource, **kwargs):
    transaction.on_commit(lambda: _update_local_idp_of_tenant(instance))


def _update_local_idp_of_tenant(data_source: DataSource):
    """
    更新租户的本地账密登录认证源
    对于每个租户，如果有本地数据源，则必须有本地账密认证源
    该函数主要是根据本地数据源(status和enable_account_password_login)的变化更新租户的本地账密认证源配置和状态
    """
    # 非本地数据源不需要默认认证源
    if not data_source.is_local:
        return

    # 获取本地账密认证的插件
    plugin = IdpPlugin.objects.get(id=BuiltinIdpPluginEnum.LOCAL)
    # 获取租户下的本地账密认证源
    idp, __ = Idp.objects.get_or_create(
        owner_tenant_id=data_source.owner_tenant_id, plugin=plugin, defaults={"name": _("本地账密")}
    )

    # 判断数据源 status和enable_account_password_login ，确定是否使用账密登录
    plugin_cfg = data_source.get_plugin_cfg()
    assert isinstance(plugin_cfg, LocalDataSourcePluginConfig)

    enable_login = bool(data_source.status == DataSourceStatus.ENABLED and plugin_cfg.enable_account_password_login)

    # 根据数据源是否使用账密登录，修改认证源配置
    idp_plugin_cfg = LocalIdpPluginConfig(**idp.plugin_config)
    data_source_match_rules = DataSourceMatchRuleList.validate_python(idp.data_source_match_rules)

    # 对于启用登录，则需要添加进配置
    if enable_login and data_source.id not in idp_plugin_cfg.data_source_ids:
        idp_plugin_cfg.data_source_ids.append(data_source.id)
        data_source_match_rules.append(
            gen_data_source_match_rule_of_local(data_source.id),
        )
    # 对于不启用登录，则需要删除配置
    if not enable_login and data_source.id in idp_plugin_cfg.data_source_ids:
        idp_plugin_cfg.data_source_ids = [i for i in idp_plugin_cfg.data_source_ids if i != data_source.id]
        data_source_match_rules = [i for i in data_source_match_rules if i.data_source_id != data_source.id]

    # 保存
    idp.plugin_config = idp_plugin_cfg.model_dump()
    idp.data_source_match_rules = [i.model_dump() for i in data_source_match_rules]
    idp.status = IdpStatus.ENABLED if idp_plugin_cfg.data_source_ids else IdpStatus.DISABLED
    idp.save(update_fields=["plugin_config", "data_source_match_rules", "status", "updated_at"])
