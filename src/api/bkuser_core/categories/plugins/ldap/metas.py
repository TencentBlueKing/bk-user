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
from bkuser_core.categories.plugins.base import DepartmentMeta, ProfileMeta


class LdapDepartmentMeta(DepartmentMeta):
    update_exclude_fields = ["category_id", "code"]
    unique_key_field = "code"
    use_bulk = True


class LdapProfileMeta(ProfileMeta):
    unique_key_field = "username"
    update_exclude_fields = ["code", "username"]
