# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
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
import logging
import os

from django.db import migrations
from django.utils import timezone

from bkuser.common.constants import PERMANENT_TIME
from bkuser.common.hashers import make_password
from bkuser.plugins.base import get_default_plugin_cfg
from bkuser.plugins.constants import DataSourcePluginEnum
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.idp_plugins.local.plugin import LocalIdpPluginConfig
from bkuser.apps.idp.data_models import gen_data_source_match_rule_of_local
from bkuser.apps.tenant.constants import DEFAULT_TENANT_USER_VALIDITY_PERIOD_CONFIG, BuiltInTenantIDEnum
from bkuser.apps.data_source.constants import DataSourceTypeEnum

logger = logging.getLogger(__name__)


def forwards_func(apps, schema_editor):
    """初始化本地数据源插件"""
    if os.getenv("SKIP_INIT_DEFAULT_TENANT", "false").lower() == "true":
        logger.info("skip initialize first tenant & data source")
        return

    admin_username = os.getenv("INITIAL_ADMIN_USERNAME")
    admin_password = os.getenv("INITIAL_ADMIN_PASSWORD")
    if not (admin_username and admin_password):
        raise RuntimeError("INITIAL_ADMIN_USERNAME and INITIAL_ADMIN_PASSWORD must be set in environment variables")

    # 根据是否开启多租户模式，选择初始化的租户（运营租户或默认租户）
    enable_mutil_tenant_mode = os.getenv("ENABLE_MUTIL_TENANT_MODE", "false").lower() == "true"
    if enable_mutil_tenant_mode:
        first_tenant_id = BuiltInTenantIDEnum.SYSTEM
        first_tenant_name = BuiltInTenantIDEnum.get_choice_label(BuiltInTenantIDEnum.SYSTEM)
    else:
        first_tenant_id = BuiltInTenantIDEnum.DEFAULT
        first_tenant_name = BuiltInTenantIDEnum.get_choice_label(BuiltInTenantIDEnum.DEFAULT)

    logger.info(
        "start initialize first tenant[%s] & data source with admin user [%s]...",
        first_tenant_id,
        admin_username,
    )

    Tenant = apps.get_model("tenant", "Tenant")
    TenantUser = apps.get_model("tenant", "TenantUser")
    TenantManager = apps.get_model("tenant", "TenantManager")
    TenantUserValidityPeriodConfig = apps.get_model("tenant", "TenantUserValidityPeriodConfig")
    DataSource = apps.get_model("data_source", "DataSource")
    DataSourceUser = apps.get_model("data_source", "DataSourceUser")
    LocalDataSourceIdentityInfo = apps.get_model("data_source", "LocalDataSourceIdentityInfo")
    Idp = apps.get_model("idp", "Idp")

    first_tenant = Tenant.objects.create(id=first_tenant_id, name=first_tenant_name, is_default=True)
    # 租户配置
    TenantUserValidityPeriodConfig.objects.create(tenant=first_tenant, **DEFAULT_TENANT_USER_VALIDITY_PERIOD_CONFIG)

    data_source = DataSource.objects.create(
        type=DataSourceTypeEnum.BUILTIN_MANAGEMENT,
        owner_tenant_id=first_tenant.id,
        plugin_id=DataSourcePluginEnum.LOCAL,
        plugin_config=get_default_plugin_cfg(DataSourcePluginEnum.LOCAL).model_dump(),
    )

    data_source_user = DataSourceUser.objects.create(
        data_source=data_source,
        code=admin_username,
        username=admin_username,
        full_name=admin_username,
    )
    LocalDataSourceIdentityInfo.objects.create(
        user=data_source_user,
        password=make_password(admin_password),
        password_updated_at=timezone.now(),
        password_expired_at=PERMANENT_TIME,
        data_source=data_source,
        username=admin_username,
    )
    tenant_user = TenantUser.objects.create(
        tenant=first_tenant,
        data_source_user=data_source_user,
        data_source=data_source,
        # FIXME (nan): 应该使用 TenantUserIDGenerator 生成，但相关表是在该 migration 之后创建的，会导致异常
        #  思考：是否初始化数据不应该使用 migration(只做表变更？)，而是使用 Django Command 呢？那如何记录是否初始化过了呢？
        id=admin_username,
    )
    TenantManager.objects.create(tenant=first_tenant, tenant_user=tenant_user)

    Idp.objects.create(
        name="Administrator",
        plugin_id=BuiltinIdpPluginEnum.LOCAL,
        owner_tenant_id=first_tenant.id,
        plugin_config=LocalIdpPluginConfig(data_source_ids=[data_source.id]).model_dump(),
        data_source_match_rules=[gen_data_source_match_rule_of_local(data_source.id).model_dump()],
        data_source_id=data_source.id,
    )

    logger.info(
        "initialize first tenant & data source with admin user [%s] success",
        admin_username,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("tenant", "0002_init_builtin_user_fields"),
        ("data_source", "0002_init_builtin_data_source_plugin"),
        ("idp", "0002_init_builtin_idp_plugin"),
    ]

    operations = [migrations.RunPython(forwards_func)]
