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
from typing import Dict

import pytest
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.departments.models import Department
from bkuser_core.profiles.models import DynamicFieldInfo, Profile


def make_simple_profile(username: str, force_create_params: Dict = None):
    """创建一个简单的人员"""
    default_category = ProfileCategory.objects.get_default()
    default_create_params = {
        "username": username,
        "display_name": username.upper(),
        "email": f"{username}@test.com",
        "telephone": "12345",
        "category_id": default_category.id,
        "domain": default_category.domain,
    }

    default_create_params.update(force_create_params or {})
    return Profile.objects.create(**default_create_params)


def make_simple_department(name: str, parent_id: int = None, force_create_params: Dict = None):
    """创建一个简单的组织"""
    default_category = ProfileCategory.objects.get_default()
    default_create_params = {"name": name, "parent_id": parent_id, "category_id": default_category.id}

    default_create_params.update(force_create_params or {})
    d = Department.objects.create(**default_create_params)
    # 只添加 parent，mptt 树需要重建
    Department.tree_objects.partial_rebuild(tree_id=d.tree_id)

    return d


def make_simple_category(
    domain: str,
    display_name: str,
    type: str = "local",
    force_create_params: Dict = None,
):
    """创建一个简单的目录"""
    default_create_params = {"domain": domain, "display_name": display_name, "type": type}

    default_create_params.update(force_create_params or {})
    c = ProfileCategory.objects.create(**default_create_params)
    return c


def attach_pd_relation(profile: Profile, department: Department):
    """简单关联人员和部门"""
    department.add_profile(profile)


def make_simple_dynamic_field(name: str, force_create_params: Dict = None):
    """创建一个简单的动态字段"""
    default_create_params = {
        "name": name,
        "builtin": False,
        "order": DynamicFieldInfo.objects.get_max_order() + 1,
        "display_name": name,
    }
    default_create_params.update(force_create_params or {})
    d = DynamicFieldInfo.objects.create(**default_create_params)
    return d


def get_one_object(object_name: str, **kwargs):
    """获取满足条件的单个数据对象"""
    str_to_object = {}
    for support_object in [Profile, ProfileCategory, Department]:
        str_to_object[support_object.__name__.lower()] = support_object
    if object_name not in str_to_object:
        pytest.fail("only support %s object name now" % str_to_object.keys(), pytrace=False)
    return str_to_object[object_name].objects.get(**kwargs)
