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

DFT_RANDOM_CHARACTER_SET = "abcdefghijklmnopqrstuvwxyz0123456789"


def generate_random_string(length=16, chars=DFT_RANDOM_CHARACTER_SET):
    rand = random.SystemRandom()
    return "".join(rand.choice(chars) for _ in range(length))
