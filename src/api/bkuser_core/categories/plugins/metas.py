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
from bkuser_core.common.db_sync import SyncModelMeta
from bkuser_core.departments.models import Department, DepartmentThroughModel
from bkuser_core.profiles.models import LeaderThroughModel, Profile


class ProfileMeta(SyncModelMeta):
    target_model = Profile
    table_name = "profiles_profile"
    update_exclude_fields = ["username", "category_id", "domain"]
    unique_key_field = "username"


class LeaderProfileMeta(SyncModelMeta):
    target_model = LeaderThroughModel
    is_relation_table = True
    table_name = "profiles_profile_leader"


class DepartmentMeta(SyncModelMeta):
    target_model = Department
    use_bulk = False
    table_name = "departments_department"
    update_exclude_fields = ["name", "category_id"]


class DepartmentProfileMeta(SyncModelMeta):
    target_model = DepartmentThroughModel
    is_relation_table = True
    table_name = "departments_department_profiles"
