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

from bkuser.apps.data_source.models import DataSourceDepartment, DataSourceUser, DataSourceUserLeaderRelation
from tests.test_utils.helpers import generate_random_string


def generate_data_source_username():
    pattern = r"^[a-za-z][a-za-z0-9._-]{2,31}"
    while True:
        # 生成随机字符串
        username = "".join(random.choices(string.ascii_letters + string.digits + "._-", k=random.randint(3, 32)))
        # 判断是否符合正则表达式
        if re.match(pattern, username):
            return username


def create_data_source_user(data_source_id) -> DataSourceUser:
    return DataSourceUser.objects.create(
        full_name=generate_random_string(),
        username=generate_random_string(),
        phone="13000000000",
        data_source_id=data_source_id,
    )



def create_data_source_department(data_source_id) -> DataSourceDepartment:
    return DataSourceDepartment.objects.create(
        name=generate_random_string(), data_source_id=data_source_id
    )



def create_data_source_user_leader(user) -> DataSourceUser:
    leader = create_data_source_user(data_source_id=user.date_source_id)
    DataSourceUserLeaderRelation.objects.create(user=user, leader=leader)
    return leader
