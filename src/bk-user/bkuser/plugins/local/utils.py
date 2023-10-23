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
from hashlib import sha256


def gen_code(org: str) -> str:
    # 本地数据源数据没有提供部门 code 的方式，
    # 因此使用 sha256 计算以避免冲突，也便于后续插入 DB 时进行比较
    # 注意：本地数据源用户 code 就是 username，不需要额外计算 code
    return sha256(org.encode("utf-8")).hexdigest()
