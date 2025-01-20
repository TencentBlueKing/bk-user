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

import datetime
from typing import Any, Dict, List

from django.db import transaction
from django.utils import timezone

from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceUser,
    DataSourceUserDeprecatedPasswordRecord,
    LocalDataSourceIdentityInfo,
)
from bkuser.apps.tenant.models import TenantDepartment
from bkuser.common.constants import PERMANENT_TIME
from bkuser.common.hashers import make_password


class DataSourceUserHandler:
    @staticmethod
    def update_password(
        data_source_user: DataSourceUser,
        password: str,
        valid_days: int,
        operator: str,
    ):
        """
        更新某个用户的密码
        """
        identify_info = LocalDataSourceIdentityInfo.objects.get(user=data_source_user)
        deprecated_password = identify_info.password

        with transaction.atomic():
            identify_info.password = make_password(password)
            identify_info.password_updated_at = timezone.now()
            # 注意：更新密码会重置有效期
            if valid_days < 0:
                identify_info.password_expired_at = PERMANENT_TIME
            else:
                identify_info.password_expired_at = timezone.now() + datetime.timedelta(days=valid_days)

            identify_info.save(update_fields=["password", "password_updated_at", "password_expired_at", "updated_at"])

            DataSourceUserDeprecatedPasswordRecord.objects.create(
                user=data_source_user, password=deprecated_password, operator=operator
            )

    @staticmethod
    def batch_update_password(
        data_source_users: List[DataSourceUser],
        password: str,
        valid_days: int,
        operator: str,
    ):
        """批量更新用户的密码"""

        identify_infos = LocalDataSourceIdentityInfo.objects.filter(user__in=data_source_users)
        user_id_to_cur_password_map = {info.user_id: info.password for info in identify_infos}

        # 记录历史使用密码
        deprecated_password_records = [
            DataSourceUserDeprecatedPasswordRecord(
                user=user,
                password=user_id_to_cur_password_map.get(user.id, ""),
                operator=operator,
            )
            for user in data_source_users
        ]

        now = timezone.now()
        password_expired_at = now + datetime.timedelta(days=valid_days) if valid_days >= 0 else PERMANENT_TIME

        # Note：虽然原始密码相同，但是 make_password 中进行了加盐操作，所以每个用户的密码都必须单独 make_password，
        #  这样才能保证 DB 存储的加密串不一样。
        #  make_password 是一个耗时操作；根据测试，处理 100 个密码的平均耗时为 4.8382 秒
        for info in identify_infos:
            info.password = make_password(password)
            info.password_updated_at = now
            info.password_expired_at = password_expired_at

        with transaction.atomic():
            # 批量创建用户的历史使用密码记录
            DataSourceUserDeprecatedPasswordRecord.objects.bulk_create(deprecated_password_records, batch_size=250)

            LocalDataSourceIdentityInfo.objects.bulk_update(
                identify_infos,
                fields=["password", "password_updated_at", "updated_at"],
                batch_size=250,
            )


class DataSourceDepartmentHandler:
    @staticmethod
    def get_dept_ancestors(dept_id: int) -> List[int]:
        """
        获取某个部门的祖先部门 ID 列表
        """
        relation = DataSourceDepartmentRelation.objects.filter(department_id=dept_id).first()
        # 若该部门不存在祖先节点，则返回空列表
        if not relation:
            return []
        # 返回的祖先部门默认以降序排列，从根祖先部门 -> 父部门
        return list(relation.get_ancestors().values_list("department_id", flat=True))

    @staticmethod
    def list_dept_infos_with_parent(tenant_depts: List[TenantDepartment]) -> List[Dict[str, Any]]:
        """
        获取部门信息（包含 parent_id）
        """

        # 预加载部门对应的租户部门
        tenant_dept_id_map = {
            (data_source_dept_id, tenant_id): dept_id
            for (data_source_dept_id, tenant_id, dept_id) in TenantDepartment.objects.values_list(
                "data_source_department_id", "tenant_id", "id"
            )
        }

        # 获取数据源部门 ID
        data_source_dept_ids = {dept.data_source_department_id for dept in tenant_depts}

        # 预加载部门对应的名称
        dept_name_map = dict(
            DataSourceDepartment.objects.filter(id__in=data_source_dept_ids).values_list("id", "name")
        )

        # 组装数据
        return [
            {
                "id": dept.id,
                "name": dept_name_map[dept.data_source_department_id],
                "parent_id": tenant_dept_id_map.get(
                    (dept.data_source_department.department_relation.parent_id, dept.tenant_id)
                ),
            }
            for dept in tenant_depts
        ]
