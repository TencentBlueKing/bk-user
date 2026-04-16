# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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

from bkuser.apps.data_source.constants import DataSourceTypeEnum, DataSourceUsernameGenerateRule
from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceSensitiveInfo,
    DataSourceUser,
    DataSourceUserLeaderRelation,
    DataSourceUsernameGenerateConfig,
    DepartmentRelationMPTTTree,
)
from bkuser.apps.tenant.models import (
    TenantDepartment,
    TenantDepartmentIDRecord,
    TenantUser,
    TenantUserIDGenerateConfig,
    TenantUserIDRecord,
)


class DataSourceUsernameHandler:
    @staticmethod
    def generate(data_source: DataSource, username: str) -> str:
        """根据配置生成最终用户名"""
        cfg = data_source.username_generate_config
        if cfg.rule == DataSourceUsernameGenerateRule.ADD_AFFIX:
            return f"{cfg.prefix}{username}{cfg.suffix}"
        return username

    @staticmethod
    def parse(data_source: DataSource, username: str) -> str:
        """根据配置解析出原始用户名"""
        cfg = data_source.username_generate_config
        if cfg.rule == DataSourceUsernameGenerateRule.ADD_AFFIX:
            if cfg.prefix and username.startswith(cfg.prefix):
                username = username[len(cfg.prefix) :]
            if cfg.suffix and username.endswith(cfg.suffix):
                username = username[: -len(cfg.suffix)]
        return username

    @staticmethod
    def is_username_affix_exists(tenant_id: str, prefix: str, suffix: str, exclude_id: int | None = None) -> bool:
        """校验同租户下 ADD_AFFIX 策略的用户名前后缀唯一性"""
        qs = DataSource.objects.filter(owner_tenant_id=tenant_id, type=DataSourceTypeEnum.REAL)
        if exclude_id:
            qs = qs.exclude(id=exclude_id)

        return qs.filter(
            username_generate_config__rule=DataSourceUsernameGenerateRule.ADD_AFFIX,
            username_generate_config__prefix=prefix,
            username_generate_config__suffix=suffix,
        ).exists()

    @staticmethod
    def is_username_exists(
        data_source_ids: List[int], username: str, excluded_data_source_user_id: int | None = None
    ) -> bool:
        queryset = DataSourceUser.objects.filter(data_source_id__in=data_source_ids, username=username)
        if excluded_data_source_user_id:
            queryset = queryset.exclude(id=excluded_data_source_user_id)
        return queryset.exists()


class DataSourceHandler:
    @staticmethod
    def delete_data_source_and_related_resources(data_source: DataSource) -> None:
        """重要：必须在事务内调用该方法"""

        # ======== 删除租户相关模型数据 ========
        # 1. 删除租户部门数据
        TenantDepartment.objects.filter(data_source=data_source).delete()
        # 2. 删除租户用户数据
        TenantUser.objects.filter(data_source=data_source).delete()
        # 3. 删除相关的 ID 生成配置
        TenantUserIDGenerateConfig.objects.filter(data_source=data_source).delete()
        # 4. 删除租户用户 ID 映射记录
        TenantUserIDRecord.objects.filter(data_source=data_source).delete()
        # 5. 删除租户部门 ID 映射记录
        TenantDepartmentIDRecord.objects.filter(data_source=data_source).delete()

        # ======== 删除数据源相关模型数据 ========
        # 1. 删除部门 - 用户关系
        DataSourceDepartmentUserRelation.objects.filter(data_source=data_source).delete()
        # 2. 删除部门 - 部门关系
        DataSourceDepartmentRelation.objects.filter(data_source=data_source).delete()
        # 3. 删除数据源部门
        DataSourceDepartment.objects.filter(data_source=data_source).delete()
        # 4. 删除 Leader - 用户关系
        DataSourceUserLeaderRelation.objects.filter(data_source=data_source).delete()
        # 5. 删除数据源用户（注：密码 & 废弃密码记录会级联删除）
        DataSourceUser.objects.filter(data_source=data_source).delete()
        # 6. 删除 MPTT 树
        DepartmentRelationMPTTTree.objects.filter(data_source=data_source).delete()
        # 7. 删除数据源敏感信息
        DataSourceSensitiveInfo.objects.filter(data_source=data_source).delete()
        # 8. 删除数据源用户名生成配置
        DataSourceUsernameGenerateConfig.objects.filter(data_source=data_source).delete()
        # 9. 删除数据源
        data_source.delete()
