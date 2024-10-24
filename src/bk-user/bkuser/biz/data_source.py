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

from bkuser.apps.data_source.models import (
    DataSource,
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceSensitiveInfo,
    DataSourceUser,
    DataSourceUserLeaderRelation,
    DepartmentRelationMPTTTree,
)
from bkuser.apps.tenant.models import (
    TenantDepartment,
    TenantDepartmentIDRecord,
    TenantUser,
    TenantUserIDGenerateConfig,
    TenantUserIDRecord,
)


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
        # 8. 删除数据源
        data_source.delete()
