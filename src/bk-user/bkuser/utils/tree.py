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
from collections import defaultdict, deque
from typing import Generator, Hashable, List, Tuple, TypeVar

from pydantic import BaseModel


class TreeNode(BaseModel):
    id: str
    children: List["TreeNode"] = []


def build_forest_with_parent_relations(relations: List[Tuple[str, str | None]]) -> List[TreeNode]:
    """根据提供的父子关系构建树/森林，父子关系结构：(node_id, parent_id)"""
    node_map = {node_id: TreeNode(id=node_id) for node_id, _ in relations}
    roots = []
    for node_id, parent_id in relations:
        node = node_map[node_id]
        if not (parent_id and parent_id in node_map):
            roots.append(node)
            continue

        node_map[parent_id].children.append(node)

    return roots


def bfs_traversal_tree(root: TreeNode) -> Generator[TreeNode, None, None]:
    """广度优先遍历树，确保父节点都在子节点之前"""
    queue = [root]
    while queue:
        node = queue.pop(0)
        yield node
        queue.extend(node.children)


T = TypeVar("T", bound=Hashable)


class Tree:
    def __init__(self, pairs: List[Tuple[T, T | None]]):
        """
        :param pairs: List[(node, parent_node), ...]
        """
        self.parent_map = {}
        self.children_map = defaultdict(list)
        # 构建 parent 和 children 关系映射
        for child, parent in pairs:
            if parent is None:
                continue

            self.parent_map[child] = parent
            self.children_map[parent].append(child)

    def get_parent(self, node: T) -> T | None:
        """
        获取父亲
        时间复杂度：O(1)
        """
        return self.parent_map.get(node)

    def get_ancestors(self, node: T, include_self: bool = False) -> List[T]:
        """
        获取祖先
        时间复杂度：O(deep), deep 代表 node 在树的深度
        """
        ancestors = [node] if include_self else []
        while node in self.parent_map:
            node = self.parent_map[node]

            # 避免有环导致死循环
            if node in ancestors:
                break

            ancestors.append(node)

        # 反转，从根开始
        ancestors.reverse()

        return ancestors

    def get_children(self, node: T) -> List[T]:
        """
        获取孩子
        时间复杂度：O(1)
        """
        return self.children_map[node]

    def get_descendants(self, node: T, include_self: bool = False) -> List[T]:
        """
        获取子孙
        最大时间复杂度：O(N)，N 表示子孙数量
        """
        descendants = [node] if include_self else []

        # BFS 查找子孙
        q = deque([node])
        while q:
            n = q.popleft()
            children = self.children_map[n]
            if children:
                descendants.extend(children)
                q.extend(children)

        return descendants
