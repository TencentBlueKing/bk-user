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
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from bkuser.apps.data_source.constants import DataSourceStatus
from bkuser.apps.data_source.models import DataSource
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.idp_plugins.local.implement import LocalIdpPluginConfig
from bkuser.plugins.local.models import LocalDataSourcePluginConfig

from .constants import IdpStatus
from .data_models import DataSourceMatchRule
from .models import Idp, IdpPlugin


@receiver(post_save, sender=DataSource)
def initial_local_idp_of_tenant(sender, instance: DataSource, **kwargs):
    # 非本地数据源不需要默认认证源
    if not instance.is_local:
        return

    # 获取本地账密认证的插件
    plugin = IdpPlugin.objects.get(id=BuiltinIdpPluginEnum.LOCAL)
    # 获取租户下的本地账密认证源
    idp = Idp.objects.filter(owner_tenant_id=instance.owner_tenant_id, plugin=plugin).first()
    if idp is None:
        idp = Idp.objects.create(name=_("本地账密"), owner_tenant_id=instance.owner_tenant_id, plugin=plugin)

    # 当前数据源（1）本身是否启用状态（2）是否启用开启账密登录
    plugin_cfg = LocalDataSourcePluginConfig(**instance.plugin_config)
    enable_login = bool(instance.status == DataSourceStatus.ENABLED and plugin_cfg.enable_account_password_login)

    idp_plugin_cfg = LocalIdpPluginConfig(**idp.plugin_config)
    data_source_match_rules = DataSourceMatchRule.to_rules(idp.data_source_match_rules)
    # 对于启动登录，则需要添加进配置
    if enable_login and instance.id not in idp_plugin_cfg.data_source_ids:
        idp_plugin_cfg.data_source_ids.append(instance.id)
        data_source_match_rules.append(
            DataSourceMatchRule(source_field="id", data_source_id=instance.id, target_field="id")
        )
    # 对于不启用登录，则需要删除配置
    if not enable_login and instance.id in idp_plugin_cfg.data_source_ids:
        idp_plugin_cfg.data_source_ids = [i for i in idp_plugin_cfg.data_source_ids if i != instance.id]
        data_source_match_rules = [i for i in data_source_match_rules if i.data_source_id != instance.id]

    # 保存
    idp.plugin_config = idp_plugin_cfg.model_dump()
    idp.data_source_match_rules = [i.model_dump() for i in data_source_match_rules]
    idp.status = IdpStatus.ENABLED if idp_plugin_cfg.data_source_ids else IdpStatus.DISABLED
    idp.save()
