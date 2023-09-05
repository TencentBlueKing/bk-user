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
import random
from typing import List

from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)


def create_data_source_departments_with_relationship(data_source_id: int):
    """
    创建数据源部门，并以首个对象为其余对象的父部门
    """
    data_source_departments: List[DataSourceDepartment] = []
    for i in range(10):
        department = DataSourceDepartment.objects.create(data_source_id=data_source_id, name=f"fake_dept_{i}")
        data_source_departments.append(department)

    # 添加部门关系
    root = DataSourceDepartmentRelation.objects.create(
        department=data_source_departments[0], data_source_id=data_source_id
    )
    for item in data_source_departments[1:]:
        DataSourceDepartmentRelation.objects.create(department=item, data_source_id=data_source_id, parent=root)
    return data_source_departments


def create_data_source_users_with_relationship(data_source_id: int, department_ids: List[int]):
    """
    创建数据源用户，并以首个对象为其余对象的上级, 随机关联部门
    """
    data_source_users: List[DataSourceUser] = []
    for i in range(10):
        fake_user = DataSourceUser.objects.create(
            full_name=f"fake-user-{i}", username=f"fake-user-{i}", phone="1312345678", data_source_id=data_source_id
        )
        data_source_users.append(fake_user)

    # 添加上下级关系
    leader = data_source_users[0]
    for user in data_source_users[1:]:
        DataSourceUserLeaderRelation.objects.get_or_create(user=user, leader=leader)

    for item in data_source_users:
        DataSourceDepartmentUserRelation.objects.get_or_create(user=item, department_id=random.choice(department_ids))
    return data_source_users
