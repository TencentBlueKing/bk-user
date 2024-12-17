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
import string

from nanoid import generate


def generate_nanoid(size: int = 16) -> str:
    """生成默认长度为 16 的 nanoid，字符集为小写字母 + 数字"""

    # Q：为什么 nanoid 的长度选择 16，而不是默认的 21？
    # A：16 字符长度的 nanoid 冲突概率能够满足大部分场景，且长度更短更易于存储，以及提升 DB 查询性能
    # Q：为什么 nanoid 字符集选择小写字母 + 数字？
    # A：避免 DB 大小写字母敏感引起冲突
    return generate(alphabet=string.digits + string.ascii_lowercase, size=size)
