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
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.models import TenantUserCustomField


@pytest.fixture()
def tenant_user_custom_fields(default_tenant) -> List[TenantUserCustomField]:
    age_field, _ = TenantUserCustomField.objects.get_or_create(
        tenant=default_tenant,
        name="age",
        defaults={
            "display_name": "年龄",
            "data_type": UserFieldDataType.NUMBER,
            "required": False,
            "default": 0,
        },
    )
    gender_field, _ = TenantUserCustomField.objects.get_or_create(
        tenant=default_tenant,
        name="gender",
        defaults={
            "display_name": "性别",
            "data_type": UserFieldDataType.ENUM,
            "required": True,
            "default": "male",
            "options": {
                "male": "男",
                "female": "女",
                "other": "其他",
            },
        },
    )
    region_field, _ = TenantUserCustomField.objects.get_or_create(
        tenant=default_tenant,
        name="region",
        defaults={
            "display_name": "籍贯",
            "data_type": UserFieldDataType.STRING,
            "required": True,
        },
    )
    return [age_field, gender_field, region_field]
