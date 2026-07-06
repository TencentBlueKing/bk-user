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
import pytest
from bkuser.apps.data_source.models import (
    DataSourceDepartment,
    DataSourceDepartmentUserRelation,
    DataSourceUser,
    DataSourceUserLeaderRelation,
)
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestDepartmentUserRelationBatchCreate:
    def test_standard(self, api_client, full_local_data_source):
        ds_user = DataSourceUser.objects.filter(data_source=full_local_data_source).first()
        ds_dept = DataSourceDepartment.objects.filter(data_source=full_local_data_source).first()

        resp = api_client.post(
            reverse(
                "open_provider.department_user_relation.batch",
                kwargs={"data_source_id": full_local_data_source.id},
            ),
            data={
                "relations": [
                    {"user_id": ds_user.code, "department_id": ds_dept.code},
                ]
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert DataSourceDepartmentUserRelation.objects.filter(
            user_id=ds_user.id,
            department_id=ds_dept.id,
        ).exists()


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestDepartmentUserRelationBatchDelete:
    def test_standard(self, api_client, full_local_data_source):
        ds_user = DataSourceUser.objects.filter(data_source=full_local_data_source).first()

        existing_rel = DataSourceDepartmentUserRelation.objects.filter(user_id=ds_user.id).first()
        if not existing_rel:
            return

        ds_dept = DataSourceDepartment.objects.get(id=existing_rel.department_id)

        resp = api_client.delete(
            reverse(
                "open_provider.department_user_relation.batch",
                kwargs={"data_source_id": full_local_data_source.id},
            ),
            data={
                "relations": [
                    {"user_id": ds_user.code, "department_id": ds_dept.code},
                ]
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not DataSourceDepartmentUserRelation.objects.filter(
            user_id=ds_user.id,
            department_id=ds_dept.id,
        ).exists()


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestUserLeaderRelationBatchCreate:
    def test_standard(self, api_client, full_local_data_source):
        ds_users = DataSourceUser.objects.filter(data_source=full_local_data_source)[:2]

        if len(ds_users) < 2:
            return

        user = ds_users[0]
        leader = ds_users[1]

        resp = api_client.post(
            reverse(
                "open_provider.user_leader_relation.batch",
                kwargs={"data_source_id": full_local_data_source.id},
            ),
            data={
                "relations": [
                    {"user_id": user.code, "leader_ids": [leader.code]},
                ]
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert DataSourceUserLeaderRelation.objects.filter(
            user_id=user.id,
            leader_id=leader.id,
        ).exists()


@pytest.mark.usefixtures("_init_tenant_users_depts")
class TestUserLeaderRelationBatchDelete:
    def test_standard(self, api_client, full_local_data_source):
        ds_users = DataSourceUser.objects.filter(data_source=full_local_data_source)[:2]

        if len(ds_users) < 2:
            return

        user = ds_users[0]
        leader = ds_users[1]

        DataSourceUserLeaderRelation.objects.get_or_create(
            user_id=user.id,
            leader_id=leader.id,
            data_source=full_local_data_source,
        )

        resp = api_client.delete(
            reverse(
                "open_provider.user_leader_relation.batch",
                kwargs={"data_source_id": full_local_data_source.id},
            ),
            data={
                "relations": [
                    {"user_id": user.code, "leader_ids": [leader.code]},
                ]
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not DataSourceUserLeaderRelation.objects.filter(
            user_id=user.id,
            leader_id=leader.id,
        ).exists()
