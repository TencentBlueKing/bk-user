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

import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestAuditRecordListApi:
    def test_audit_record_list(self, api_client, audit_records):
        resp = api_client.get(reverse("audit.list"))

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 4

    def test_audit_record_list_filter_by_creator(self, api_client, bk_user, audit_records):
        resp = api_client.get(reverse("audit.list"), data={"creator": bk_user.username})

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 4
        assert all(record["creator"] == bk_user.username for record in resp.data["results"])

    def test_audit_record_list_filter_by_operation(self, api_client, audit_records):
        resp = api_client.get(reverse("audit.list"), data={"operation": "create_data_source"})

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["operation"] == "create_data_source"

    def test_audit_record_list_filter_by_object_type(self, api_client, audit_records):
        resp = api_client.get(reverse("audit.list"), data={"object_type": "data_source"})

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 4
        assert all(record["object_type"] == "data_source" for record in resp.data["results"])

    def test_audit_record_list_filter_by_object_name(self, api_client, audit_records):
        resp = api_client.get(reverse("audit.list"), data={"object_name": "DataSource1"})

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["object_name"] == "DataSource1"

    def test_audit_record_list_filter_by_fuzzy_object_name(self, api_client, audit_records):
        resp = api_client.get(reverse("audit.list"), data={"object_name": "DataSource"})

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 4
        assert all("DataSource" in record["object_name"] for record in resp.data["results"])

    def test_audit_record_list_filter_by_object_type_and_name(self, api_client, audit_records):
        resp = api_client.get(reverse("audit.list"), data={"object_type": "data_source", "object_name": "DataSource1"})

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["object_type"] == "data_source"
        assert resp.data["results"][0]["object_name"] == "DataSource1"

    def test_audit_record_list_filter_by_object_type_and_operation(self, api_client, audit_records):
        resp = api_client.get(
            reverse("audit.list"), data={"object_type": "data_source", "operation": "create_data_source"}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["object_type"] == "data_source"
        assert resp.data["results"][0]["operation"] == "create_data_source"

    def test_audit_record_list_filter_by_creator_and_operation(self, api_client, bk_user, audit_records):
        resp = api_client.get(
            reverse("audit.list"), data={"creator": bk_user.username, "operation": "create_data_source"}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["creator"] == bk_user.username
        assert resp.data["results"][0]["operation"] == "create_data_source"

    def test_audit_record_list_filter_by_creator_and_object_type(self, api_client, bk_user, audit_records):
        resp = api_client.get(reverse("audit.list"), data={"creator": bk_user.username, "object_type": "data_source"})

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 4
        assert all(
            record["creator"] == bk_user.username and record["object_type"] == "data_source"
            for record in resp.data["results"]
        )

    def test_audit_record_list_filter_by_creator_and_object_name(self, api_client, bk_user, audit_records):
        resp = api_client.get(reverse("audit.list"), data={"creator": bk_user.username, "object_name": "DataSource1"})

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["creator"] == bk_user.username
        assert resp.data["results"][0]["object_name"] == "DataSource1"

    def test_audit_record_list_filter_by_operation_and_object_name(self, api_client, audit_records):
        resp = api_client.get(
            reverse("audit.list"), data={"operation": "create_data_source", "object_name": "DataSource1"}
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["operation"] == "create_data_source"
        assert resp.data["results"][0]["object_name"] == "DataSource1"

    def test_audit_record_list_filter_by_creator_object_type_and_operation(self, api_client, bk_user, audit_records):
        resp = api_client.get(
            reverse("audit.list"),
            data={"creator": bk_user.username, "object_type": "data_source", "operation": "create_data_source"},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["creator"] == bk_user.username
        assert resp.data["results"][0]["object_type"] == "data_source"
        assert resp.data["results"][0]["operation"] == "create_data_source"

    def test_audit_record_list_filter_by_creator_object_type_and_object_name(self, api_client, bk_user, audit_records):
        resp = api_client.get(
            reverse("audit.list"),
            data={"creator": bk_user.username, "object_type": "data_source", "object_name": "DataSource1"},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["creator"] == bk_user.username
        assert resp.data["results"][0]["object_type"] == "data_source"
        assert resp.data["results"][0]["object_name"] == "DataSource1"

    def test_audit_record_list_filter_by_creator_operation_and_object_name(self, api_client, bk_user, audit_records):
        resp = api_client.get(
            reverse("audit.list"),
            data={"creator": bk_user.username, "operation": "create_data_source", "object_name": "DataSource1"},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["creator"] == bk_user.username
        assert resp.data["results"][0]["operation"] == "create_data_source"
        assert resp.data["results"][0]["object_name"] == "DataSource1"

    def test_audit_record_list_filter_by_object_type_operation_and_object_name(self, api_client, audit_records):
        resp = api_client.get(
            reverse("audit.list"),
            data={"object_type": "data_source", "operation": "create_data_source", "object_name": "DataSource1"},
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["object_type"] == "data_source"
        assert resp.data["results"][0]["operation"] == "create_data_source"
        assert resp.data["results"][0]["object_name"] == "DataSource1"

    def test_audit_record_list_filter_by_creator_object_type_operation_and_object_name(
        self, api_client, bk_user, audit_records
    ):
        resp = api_client.get(
            reverse("audit.list"),
            data={
                "creator": bk_user.username,
                "object_type": "data_source",
                "operation": "create_data_source",
                "object_name": "DataSource1",
            },
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["creator"] == bk_user.username
        assert resp.data["results"][0]["object_type"] == "data_source"
        assert resp.data["results"][0]["operation"] == "create_data_source"
        assert resp.data["results"][0]["object_name"] == "DataSource1"

    def test_audit_record_list_filter_by_invalid_operation(self, api_client, audit_records):
        resp = api_client.get(reverse("audit.list"), data={"operation": "non_existent_operation"})

        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_audit_record_list_filter_by_invalid_object_type(self, api_client, audit_records):
        resp = api_client.get(reverse("audit.list"), data={"object_type": "non_existent_object_type"})

        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_audit_record_list_filter_by_non_existent_object_name(self, api_client, audit_records):
        resp = api_client.get(reverse("audit.list"), data={"object_name": "non_existent_object_name"})

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 0

    def test_audit_record_list_pagination_first_page(self, api_client, audit_records):
        resp = api_client.get(reverse("audit.list"), data={"page": 1, "page_size": 2})

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 4
        assert len(resp.data["results"]) == 2

    def test_audit_record_list_pagination_second_page(self, api_client, audit_records):
        resp = api_client.get(reverse("audit.list"), data={"page": 2, "page_size": 2})

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 4
        assert len(resp.data["results"]) == 2
