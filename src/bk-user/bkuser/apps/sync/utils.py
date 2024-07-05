# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging

from bkuser.apps.data_source.constants import TenantUserIdRuleEnum
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.sync.models import TenantUserIDGenerateConfig
from bkuser.utils.uuid import generate_uuid

logger = logging.getLogger(__name__)


def gen_tenant_user_id(target_tenant_id: str, data_source: DataSource, user: DataSourceUser) -> str:
    """根据规则生成租户用户 ID"""
    cfg = TenantUserIDGenerateConfig.objects.filter(data_source=data_source, target_tenant_id=target_tenant_id).first()
    if not cfg:
        return generate_uuid()

    if cfg.rule == TenantUserIdRuleEnum.USERNAME_WITH_DOMAIN:
        return f"{user.username}@{cfg.domain}"

    if cfg.rule == TenantUserIdRuleEnum.USERNAME:
        return user.username

    return generate_uuid()


def is_data_source_username_frozen(data_source: DataSource) -> bool:
    """数据源用户名是否不可变更"""
    return (
        TenantUserIDGenerateConfig.objects.filter(data_source=data_source)
        .exclude(rule=TenantUserIdRuleEnum.UUID4_HEX)
        .exists()
    )
