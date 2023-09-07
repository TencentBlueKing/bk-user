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
import re
import string
from typing import List

from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from tests.test_utils.helpers import generate_random_string


def generate_data_source_username():
    pattern = r"^[a-za-z][a-za-z0-9._-]{2,31}"
    while True:
        # 生成随机字符串
        username = "".join(random.choices(string.ascii_letters + string.digits + "._-", k=random.randint(3, 32)))
        # 判断是否符合正则表达式
        if re.match(pattern, username):
            return username


def create_data_source_departments(data_source) -> List[DataSourceDepartment]:
    """
    创建数据源部门
    """
    departments = [DataSourceDepartment(data_source=data_source, name=generate_random_string()) for _ in range(10)]
    DataSourceDepartment.objects.bulk_create(departments)

    return list(DataSourceDepartment.objects.filter(data_source=data_source))


def create_data_source_users(data_source, departments) -> List[DataSourceUser]:
    """
    创建数据源用户，关联首个用户为上级，随机关联部门
    """
    users = [
        DataSourceUser(
            full_name=generate_random_string(),
            username=generate_random_string(),
            email=f"{generate_random_string()}@qq.com",
            phone="13123456789",
            data_source=data_source,
        )
        for _ in range(10)
    ]
    DataSourceUser.objects.bulk_create(users)

    data_source_users = list(DataSourceUser.objects.filter(data_source=data_source))
    # 添加用户-上级关系
    user_leader_relations = [
        DataSourceUserLeaderRelation(user=data_source_user, leader=data_source_users[0])
        for data_source_user in data_source_users[1:]
    ]
    DataSourceUserLeaderRelation.objects.bulk_create(user_leader_relations)
    # 添加部门-用户关系
    user_department_relations = [
        DataSourceDepartmentUserRelation(user=data_source_user, department=random.choice(departments))
        for data_source_user in data_source_users
    ]
    DataSourceDepartmentUserRelation.objects.bulk_create(user_department_relations)

    return data_source_users
