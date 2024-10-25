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
from typing import List, Tuple

import pytest
from bkuser.utils.tree import Tree, TreeNode, bfs_traversal_tree, build_forest_with_parent_relations


def test_build_forest_with_tree_parent_relations():
    """理想情况，只有一棵树"""
    relations = [("A", None), ("B", "A"), ("C", "A"), ("D", "B"), ("E", "B")]
    roots = build_forest_with_parent_relations(relations)
    assert roots == [
        TreeNode(
            id="A",
            children=[
                TreeNode(
                    id="B",
                    children=[TreeNode(id="D"), TreeNode(id="E")],
                ),
                TreeNode(id="C"),
            ],
        )
    ]


def test_build_forest_with_forest_parent_relations():
    """森林关系测试"""
    relations = [("A", None), ("C", "B"), ("D", "B"), ("B", None)]
    roots = build_forest_with_parent_relations(relations)
    assert roots == [
        TreeNode(id="A"),
        TreeNode(id="B", children=[TreeNode(id="C"), TreeNode(id="D")]),
    ]


def test_build_forest_with_invalid_parent_relations():
    """森林关系测试，但是某父节点丢失"""
    relations = [("A", None), ("C", "B"), ("D", "B")]
    roots = build_forest_with_parent_relations(relations)
    assert roots == [TreeNode(id="A"), TreeNode(id="C"), TreeNode(id="D")]


def test_build_forest_with_empty_parent_relations():
    """空关系测试"""
    relations: List[Tuple[str, str | None]] = []
    roots = build_forest_with_parent_relations(relations)
    assert len(roots) == 0


def test_bfs_traversal_tree():
    """正常情况测试"""
    root = TreeNode(
        id="A",
        children=[
            TreeNode(id="B"),
            TreeNode(id="C"),
            TreeNode(
                id="D",
                children=[
                    TreeNode(id="E"),
                ],
            ),
        ],
    )
    nodes = list(bfs_traversal_tree(root))
    assert [n.id for n in nodes] == ["A", "B", "C", "D", "E"]


def test_bfs_traversal_tree_single():
    """单个节点测试"""
    root = TreeNode(id="A")
    nodes = list(bfs_traversal_tree(root))
    assert nodes == [root]


class TestTree:
    @pytest.fixture()
    def simple_tree(self) -> Tree:
        return Tree(
            [
                ("公司", None),
                ("部门A", "公司"),
                ("中心AA", "部门A"),
                ("小组AAA", "中心AA"),
                ("中心AB", "部门A"),
                ("小组ABA", "中心AB"),
                ("部门B", "公司"),
                ("中心BA", "部门B"),
                ("小组BAA", "中心BA"),
            ]
        )

    def test_get_parent(self, simple_tree):
        assert simple_tree.get_parent("公司") is None
        assert simple_tree.get_parent("部门A") == "公司"
        assert simple_tree.get_parent("中心AB") == "部门A"
        assert simple_tree.get_parent("小组ABA") == "中心AB"

    def test_get_ancestors(self, simple_tree):
        assert simple_tree.get_ancestors("公司") == []
        assert simple_tree.get_ancestors("部门A") == ["公司"]
        assert simple_tree.get_ancestors("小组ABA") == ["公司", "部门A", "中心AB"]
        assert simple_tree.get_ancestors("小组BAA") == ["公司", "部门B", "中心BA"]

    def test_get_ancestors_include_self(self, simple_tree):
        assert simple_tree.get_ancestors("公司", include_self=True) == ["公司"]
        assert simple_tree.get_ancestors("部门A", include_self=True) == ["公司", "部门A"]

    def test_get_children(self, simple_tree):
        assert simple_tree.get_children("公司") == ["部门A", "部门B"]
        assert simple_tree.get_children("部门A") == ["中心AA", "中心AB"]
        assert simple_tree.get_children("中心AA") == ["小组AAA"]
        assert simple_tree.get_children("小组AAA") == []

    def test_get_descendants(self, simple_tree):
        assert simple_tree.get_descendants("公司") == [
            "部门A",
            "部门B",
            "中心AA",
            "中心AB",
            "中心BA",
            "小组AAA",
            "小组ABA",
            "小组BAA",
        ]
        assert simple_tree.get_descendants("部门A") == ["中心AA", "中心AB", "小组AAA", "小组ABA"]
        assert simple_tree.get_descendants("中心AA") == ["小组AAA"]
        assert simple_tree.get_descendants("小组AAA") == []

    def test_get_descendants_include_self(self, simple_tree):
        assert simple_tree.get_descendants("中心AA", include_self=True) == ["中心AA", "小组AAA"]
        assert simple_tree.get_descendants("小组AAA", include_self=True) == ["小组AAA"]
