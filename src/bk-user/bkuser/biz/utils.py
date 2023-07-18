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
import random
import string


def gen_random_str(length):
    # 必须包含至少一个数字
    chars = string.ascii_letters + string.digits

    random_chars = [random.choice(chars) for _ in range(length)]
    if any([c.isdigit() for c in random_chars]):
        return "".join(random_chars)

    random_chars[0] = random.choice(string.digits)
    random.shuffle(random_chars)
    return "".join(random_chars)
