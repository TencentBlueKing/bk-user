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
import pytest
from bkuser.apps.idp.data_models import DataSourceMatchRule, FieldCompareRule
from django.db.models import Q

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ("source_data", "excepted_queryset"),
    [
        # valid
        (
            {"user_id": "test_username", "phone": "1234567890123"},
            (Q(data_source_id=1) & Q(username="test_username") & Q(phone="1234567890123")),
        ),
        (
            {"user_id": "test_username", "phone": "1234567890123", "email": "111@qq.com"},
            (Q(data_source_id=1) & Q(username="test_username") & Q(phone="1234567890123")),
        ),
        # invalid
        (
            {"user_id": "test_username"},
            None,
        ),
    ],
)
def test_convert_to_queryset_filter_for_source_data(source_data, excepted_queryset):
    data_source_match_rule = DataSourceMatchRule(
        data_source_id=1,
        field_compare_rules=[
            FieldCompareRule(source_field="user_id", target_field="username"),
            FieldCompareRule(source_field="phone", target_field="phone"),
        ],
    )
    queryset = data_source_match_rule.convert_to_queryset_filter(source_data)

    assert queryset == excepted_queryset


@pytest.mark.parametrize(
    ("rule", "excepted_queryset"),
    [
        # No field compare rule
        (
            DataSourceMatchRule(data_source_id=1, field_compare_rules=[]),
            None,
        ),
        # one field compare rule
        (
            DataSourceMatchRule(
                data_source_id=1,
                field_compare_rules=[FieldCompareRule(source_field="user_id", target_field="username")],
            ),
            (Q(data_source_id=1) & Q(username="test_username")),
        ),
        # Mult field compare rule
        (
            DataSourceMatchRule(
                data_source_id=1,
                field_compare_rules=[
                    FieldCompareRule(source_field="user_id", target_field="username"),
                    FieldCompareRule(source_field="phone", target_field="phone"),
                    FieldCompareRule(source_field="email", target_field="private_email"),
                ],
            ),
            (
                Q(data_source_id=1)
                & Q(username="test_username")
                & Q(phone="1234567890123")
                & Q(private_email="111@qq.com")
            ),
        ),
    ],
)
def test_convert_to_queryset_filter_for_rule(rule, excepted_queryset):
    source_data = {"user_id": "test_username", "phone": "1234567890123", "email": "111@qq.com"}

    queryset = rule.convert_to_queryset_filter(source_data)

    assert queryset == excepted_queryset
