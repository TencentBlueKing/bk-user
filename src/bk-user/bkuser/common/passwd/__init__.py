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
from .exceptions import PasswordGenerateError, PasswordStrengthError
from .generator import PasswordGenerator
from .models import PasswordRule, ValidateResult
from .validator import PasswordValidator

__all__ = [
    # 密码规则
    "PasswordRule",
    # 密码生成器
    "PasswordGenerator",
    # 密码强度校验器
    "PasswordValidator",
    # 密码校验结果
    "ValidateResult",
    # 密码强度过低异常
    "PasswordStrengthError",
    # 不合理的规则导致生成密码失败
    "PasswordGenerateError",
]
