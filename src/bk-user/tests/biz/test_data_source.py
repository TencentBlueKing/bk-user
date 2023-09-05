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

import pytest
from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from bkuser.biz.data_source import DataSourceDepartmentHandler, DataSourceUserHandler

pytestmark = pytest.mark.django_db


class TestDataSourceDepartmentHandler:
    def test_get_department_info_map_by_ids(self, local_data_source_departments: List[DataSourceDepartment]):
        departments_map = DataSourceDepartmentHandler.get_department_info_map_by_ids(
            [department.id for department in local_data_source_departments]
        )

        for item in local_data_source_departments:
            departments_info = departments_map.get(item.id)
            assert departments_info
            assert item.name == departments_info.name

            child_ids = (
                DataSourceDepartmentRelation.objects.get(department=item)
                .get_children()
                .values_list("department_id", flat=True)
            )
            for child_id in departments_info.child_ids:
                assert child_id in child_ids

    @pytest.mark.parametrize(
        "not_exist_data_source_department_ids",
        [
            [],
            [1, 2, 3],
            [11, 22, 33],
            [14, 24, 34],
        ],
    )
    def test_not_exist_get_department_info_map_by_ids(self, not_exist_data_source_department_ids: List[int]):
        departments_map = DataSourceDepartmentHandler.get_department_info_map_by_ids(
            not_exist_data_source_department_ids
        )
        assert not departments_map

    def test_get_user_department_ids_map(
        self, local_data_source_departments: List[DataSourceDepartment], local_data_source_users: List[DataSourceUser]
    ):
        user_ids = [user.id for user in local_data_source_users]

        user_department_relationship_map = DataSourceDepartmentHandler.get_user_department_ids_map(user_ids)
        for user_id in user_ids:
            department_ids = user_department_relationship_map.get(user_id)
            assert department_ids
            real_department_ids = DataSourceDepartmentUserRelation.objects.filter(user_id=user_id).values_list(
                "department_id", flat=True
            )
            for department_id in department_ids:
                assert department_id in real_department_ids

    @pytest.mark.parametrize(
        "not_exist_data_source_user_ids",
        [
            [],
            [1, 2, 3],
            [11, 22, 33],
            [14, 24, 34],
        ],
    )
    def test_not_exist_get_user_department_ids_map(self, not_exist_data_source_user_ids: List[int]):
        department_ids_map = DataSourceDepartmentHandler.get_user_department_ids_map(not_exist_data_source_user_ids)
        assert not department_ids_map


class TestDataSourceUserHandler:
    def test_get_user_leader_ids_map(self, local_data_source_users: List[DataSourceUser]):
        data_source_user_ids = [item.id for item in local_data_source_users]
        leader_ids_map = DataSourceUserHandler.get_user_leader_ids_map(data_source_user_ids)

        for user_id in data_source_user_ids:
            leader_ids = leader_ids_map.get(user_id) or []
            if not DataSourceUserLeaderRelation.objects.filter(user_id=user_id):
                assert not leader_ids
            else:
                for leader_id in leader_ids:
                    assert leader_id in DataSourceUserLeaderRelation.objects.filter(user_id=user_id).values_list(
                        "leader_id", flat=True
                    )

    @pytest.mark.parametrize(
        "not_exist_data_source_user_ids",
        [
            [],
            [11, 22, 33],
            [14, 24, 34],
        ],
    )
    def test_not_exist_get_user_leader_ids_map(self, not_exist_data_source_user_ids: List[int]):
        department_ids_map = DataSourceDepartmentHandler.get_user_department_ids_map(not_exist_data_source_user_ids)
        assert not department_ids_map
