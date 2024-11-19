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
from typing import List

import pytest
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.models import TenantUserCustomField


@pytest.fixture
def tenant_user_custom_fields(request, default_tenant) -> List[TenantUserCustomField]:
    """初始化租户用户自定义字段"""
    tenant = default_tenant
    if "random_tenant" in request.fixturenames:
        tenant = request.getfixturevalue("random_tenant")

    age_field, _ = TenantUserCustomField.objects.get_or_create(
        tenant=tenant,
        name="age",
        defaults={
            "display_name": "年龄",
            "data_type": UserFieldDataType.NUMBER,
            "required": False,
            "default": 0,
            "personal_center_visible": True,
            "personal_center_editable": False,
            "manager_editable": True,
        },
    )
    gender_field, _ = TenantUserCustomField.objects.get_or_create(
        tenant=tenant,
        name="gender",
        defaults={
            "display_name": "性别",
            "data_type": UserFieldDataType.ENUM,
            "required": True,
            "default": "male",
            "personal_center_visible": True,
            "personal_center_editable": True,
            "manager_editable": True,
            "options": [
                {
                    "id": "male",
                    "value": "男",
                },
                {
                    "id": "female",
                    "value": "女",
                },
                {
                    "id": "other",
                    "value": "其他",
                },
            ],
        },
    )
    region_field, _ = TenantUserCustomField.objects.get_or_create(
        tenant=tenant,
        name="region",
        defaults={
            "display_name": "籍贯",
            "data_type": UserFieldDataType.STRING,
            "required": True,
            "default": "china",
            "personal_center_visible": False,
            "personal_center_editable": False,
            "manager_editable": True,
        },
    )
    sport_hobby_field, _ = TenantUserCustomField.objects.get_or_create(
        tenant=tenant,
        name="sport_hobby",
        defaults={
            "display_name": "运动爱好",
            "data_type": UserFieldDataType.MULTI_ENUM,
            "required": True,
            "default": ["running", "swimming"],
            "personal_center_visible": True,
            "personal_center_editable": True,
            "manager_editable": False,
            "options": [
                {
                    "id": "running",
                    "value": "跑步",
                },
                {
                    "id": "swimming",
                    "value": "游泳",
                },
                {
                    "id": "basketball",
                    "value": "篮球",
                },
                {
                    "id": "football",
                    "value": "足球",
                },
                {
                    "id": "golf",
                    "value": "高尔夫",
                },
                {
                    "id": "cycling",
                    "value": "骑行",
                },
            ],
        },
    )
    return [age_field, gender_field, region_field, sport_hobby_field]
