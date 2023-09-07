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

import pytest
from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.biz.data_source_organization import (
    DataSourceOrganizationHandler,
    DataSourceUserBaseInfo,
    DataSourceUserDepartmentInfo,
    DataSourceUserEditableBaseInfo,
    DataSourceUserLeaderInfo,
    DataSourceUserRelationInfo,
)
from django.db import transaction

from tests.test_utils.data_source_organization import (
    create_data_source_departments,
    create_data_source_users,
    generate_data_source_username,
)
from tests.test_utils.helpers import generate_random_string

pytestmark = pytest.mark.django_db


@pytest.fixture()
def base_user_info() -> DataSourceUserBaseInfo:
    return DataSourceUserBaseInfo(
        username=generate_data_source_username(),
        full_name=generate_random_string(),
        email="test@example.com",
        phone="13000000000",
        phone_country_code="86",
    )


@pytest.fixture()
def editable_base_user_info() -> DataSourceUserEditableBaseInfo:
    return DataSourceUserEditableBaseInfo(
        full_name=generate_random_string(),
        email="test@example.com",
        phone="13000000000",
        phone_country_code="86",
        logo="",
    )


@pytest.fixture()
def relation_info() -> DataSourceUserRelationInfo:
    return DataSourceUserRelationInfo(department_ids=[11, 22], leader_ids=[33, 44])


@pytest.fixture()
def data_source_departments(local_data_source) -> List[DataSourceDepartment]:
    return create_data_source_departments(data_source=local_data_source)


@pytest.fixture()
def data_source_users(local_data_source, data_source_departments) -> List[DataSourceUser]:
    return create_data_source_users(data_source=local_data_source, departments=data_source_departments)


class TestDataSourceOrganizationHandler:
    def test_create_user(self, local_data_source, base_user_info, relation_info):
        # 创建用户
        with transaction.atomic():
            user_id = DataSourceOrganizationHandler.create_user(local_data_source, base_user_info, relation_info)

        # 验证用户是否创建成功
        user = DataSourceUser.objects.get(id=user_id)
        assert user.data_source == local_data_source
        assert user.username == base_user_info.username

        # 验证用户-部门关系是否创建成功
        department_ids = relation_info.department_ids
        relations = DataSourceDepartmentUserRelation.objects.filter(user=user)
        assert set(relations.values_list("department_id", flat=True)) == set(department_ids)

        # 验证用户-上级关系是否创建成功
        leader_ids = relation_info.leader_ids
        relations = DataSourceUserLeaderRelation.objects.filter(user=user)
        assert set(relations.values_list("leader_id", flat=True)) == set(leader_ids)

    def test_update_user_department_relations(self, data_source_users):
        # 创建用户
        user = random.choice(data_source_users)

        # 创建用户-部门关系
        department_ids = [1, 2, 3]
        relations = [
            DataSourceDepartmentUserRelation(department_id=department_id, user=user)
            for department_id in department_ids
        ]
        DataSourceDepartmentUserRelation.objects.bulk_create(relations)

        # 更新用户-部门关系
        new_department_ids = [2, 3, 4]
        DataSourceOrganizationHandler.update_user_department_relations(user, new_department_ids)

        # 验证用户-部门关系是否更新成功
        department_ids = DataSourceDepartmentUserRelation.objects.filter(user=user).values_list(
            "department_id", flat=True
        )
        assert set(department_ids) == set(new_department_ids)

    def test_update_user_leader_relations(self, data_source_users):
        user = random.choice(data_source_users)
        # 创建用户-上级关系
        leader_ids = [1, 2, 3]
        relations = [DataSourceUserLeaderRelation(leader_id=leader_id, user=user) for leader_id in leader_ids]
        DataSourceUserLeaderRelation.objects.bulk_create(relations)

        # 更新用户-上级关系
        new_leader_ids = [2, 3, 4]
        DataSourceOrganizationHandler.update_user_leader_relations(user, new_leader_ids)

        # 验证用户-上级关系是否更新成功
        leaders = DataSourceUserLeaderRelation.objects.filter(user=user).values_list("leader_id", flat=True)
        assert set(leaders) == set(new_leader_ids)

    def test_update_user(self, data_source_users, editable_base_user_info, relation_info):
        user = random.choice(data_source_users)

        # 更新用户
        with transaction.atomic():
            DataSourceOrganizationHandler.update_user(user, editable_base_user_info, relation_info)

        # 验证用户基础信息是否更新成功
        assert user.full_name == editable_base_user_info.full_name
        assert user.email == editable_base_user_info.email
        assert user.phone == editable_base_user_info.phone
        assert user.phone_country_code == editable_base_user_info.phone_country_code
        assert user.logo == editable_base_user_info.logo

        # 验证用户-部门关系是否更新成功
        department_ids = relation_info.department_ids
        relations = DataSourceDepartmentUserRelation.objects.filter(user=user)
        assert set(relations.values_list("department_id", flat=True)) == set(department_ids)

        # 验证用户-上级关系是否更新成功
        leader_ids = relation_info.leader_ids
        relations = DataSourceUserLeaderRelation.objects.filter(user=user)
        assert set(relations.values_list("leader_id", flat=True)) == set(leader_ids)

    def test_list_department_info_by_id(self, data_source_departments):
        # 获取部门信息
        department_ids = [dept.id for dept in data_source_departments]
        department_infos = DataSourceOrganizationHandler.list_department_info_by_id(department_ids)

        # 验证部门信息是否正确
        assert len(department_infos) == len(department_ids)
        for department_info in department_infos:
            assert department_info.id in department_ids
            assert department_info.name == DataSourceDepartment.objects.get(id=department_info.id).name

    def test_get_user_department_ids_map(self, data_source_users):
        # 获取用户-部门id映射
        user_ids = [user.id for user in data_source_users]
        user_department_ids_map = DataSourceOrganizationHandler.get_user_department_ids_map(user_ids)

        # 验证用户-部门id映射是否正确
        assert set(user_department_ids_map.keys()) == set(user_ids)
        for user_id, department_ids in user_department_ids_map.items():
            assert set(department_ids) == set(
                DataSourceDepartmentUserRelation.objects.filter(user_id=user_id).values_list(
                    "department_id", flat=True
                )
            )

    def test_get_user_departments_map_by_user_id(self, data_source_users):
        # 获取用户-所有归属部门信息
        user_ids = [user.id for user in data_source_users]
        user_departments_map = DataSourceOrganizationHandler.get_user_departments_map_by_user_id(user_ids)

        # 验证用户-所有归属部门信息是否正确
        assert set(user_departments_map.keys()) == set(user_ids)
        for user_id, department_infos in user_departments_map.items():
            assert list(department_infos) == [
                DataSourceUserDepartmentInfo(id=dept["department_id"], name=dept["department__name"])
                for dept in DataSourceDepartmentUserRelation.objects.filter(user_id=user_id).values(
                    "department_id", "department__name"
                )
            ]

    def test_get_user_leader_ids_map(self, data_source_users):
        # 获取用户-所有上级id关系映射
        # 由于首个用户为其余用户的上级，因此需要将该用户剔除
        user_ids = [user.id for user in data_source_users][1:]
        user_leader_ids_map = DataSourceOrganizationHandler.get_user_leader_ids_map(user_ids)

        # 验证用户-所有上级id关系映射是否正确
        assert set(user_leader_ids_map.keys()) == set(user_ids)
        for user_id, leader_ids in user_leader_ids_map.items():
            assert set(leader_ids) == set(
                DataSourceUserLeaderRelation.objects.filter(user_id=user_id).values_list("leader_id", flat=True)
            )

    def test_get_user_leaders_map_by_user_id(self, data_source_users):
        # 获取用户-所有上级信息数据
        users = data_source_users[1:]
        user_ids = [user.id for user in users]
        user_leaders_map = DataSourceOrganizationHandler.get_user_leaders_map_by_user_id(user_ids)
        # 验证用户-所有上级信息数据是否正确
        assert set(user_leaders_map.keys()) == set(user_ids)

        for user_id, leader_infos in user_leaders_map.items():
            assert list(leader_infos) == [
                DataSourceUserLeaderInfo(id=leader["leader_id"], username=leader["leader__username"])
                for leader in DataSourceUserLeaderRelation.objects.filter(user_id=user_id).values(
                    "leader_id", "leader__username"
                )
            ]
