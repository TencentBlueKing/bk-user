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
from typing import List

from bkuser.apps.data_source.models import DataSourceUser
from bkuser.apps.natural_user.models import DataSourceUserNaturalUserRelation, NaturalUser
from tests.test_utils.helpers import generate_random_string


def create_natural_user_with_bind_data_source_users(data_source_users: List[DataSourceUser]) -> NaturalUser:
    natural_user = NaturalUser.objects.create(full_name=generate_random_string())
    relations = [
        DataSourceUserNaturalUserRelation(natural_user=natural_user, data_source_user=user)
        for user in data_source_users
    ]
    DataSourceUserNaturalUserRelation.objects.bulk_create(relations)
    return natural_user
