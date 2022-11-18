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

from bkuser_core.bkiam.constants import ResourceType
from bkuser_core.categories.models import Department, ProfileCategory
from bkuser_core.tests.utils import make_simple_department

pytestmark = pytest.mark.django_db


class TestResourceTypeEnum:
    # @pytest.mark.parametrize(
    #     "is_leaf, path, f, v",
    #     [
    #         (True, "/category,5/department,3440/department,3443/", "parent_id", 3443),
    #         (False, "/category,5/department,3440/department,3443/", "id", 3443),
    #         (True, "/category,5/", "category_id", 5),
    #         (False, "/category,5/", "category_id", 5),
    #         (True, "/department,3440/department,3443/", "parent_id", 3443),
    #         (False, "/department,3440/department,3443/", "id", 3443),
    #     ],
    # )
    # def test_get_key_mapping(self, is_leaf, path, f, v):
    #     key_mapping = ResourceType.get_key_mapping(ResourceType.DEPARTMENT)
    #     path_method = key_mapping["department._bk_iam_path_"]

    #     data = {"value": path}
    #     if not is_leaf:
    #         data["node_type"] = "non-leaf"

    #     f, v = path_method(data)
    #     assert f == f
    #     assert v == v

    @pytest.mark.parametrize(
        "dep_chain, expected",
        [
            (
                [1000, 1001, 1002],
                {"_bk_iam_path_": "/category,1/department,1000/department,1001/department,1002/"},
            ),
            (
                [1000],
                {"_bk_iam_path_": "/category,1/department,1000/"},
            ),
        ],
    )
    def test_get_attributes_mapping(self, dep_chain, expected):
        target_parent = None
        for d in dep_chain:
            parent_id = target_parent if not target_parent else target_parent.pk
            target_parent = make_simple_department(str(d), force_create_params={"id": d}, parent_id=parent_id)

        attributes_mapping = ResourceType.get_attributes_mapping(target_parent)
        assert attributes_mapping == expected

    def test_get_attributes_mapping_other(self):
        pc = ProfileCategory.objects.get_default()
        attributes_mapping = ResourceType.get_attributes_mapping(pc)
        assert attributes_mapping == {}

    @pytest.mark.parametrize(
        "dep_chain,expected",
        [
            (
                ["a", "b", "c"],
                [
                    ("category", "默认目录"),
                    ("department", "a"),
                    ("department", "b"),
                    ("department", "c"),
                ],
            ),
            (
                ["a", "b"],
                [("category", "默认目录"), ("department", "a"), ("department", "b")],
            ),
        ],
    )
    def test_get_resource_nodes_dep(self, dep_chain, expected):
        target_parent = None
        for d in dep_chain:
            parent_id = target_parent if not target_parent else target_parent.pk
            target_parent = make_simple_department(d, parent_id=parent_id)

        # 只添加 parent，mptt 树需要重建
        Department.tree_objects.rebuild()

        nodes = ResourceType.get_instance_resource_nodes(target_parent)
        assert [(x["type"], x["name"]) for x in nodes] == expected

    def test_get_resource_nodes_other(self):
        pc = ProfileCategory.objects.get_default()
        nodes = ResourceType.get_instance_resource_nodes(pc)
        assert [(x["type"], x["name"]) for x in nodes] == [("category", "默认目录")]
