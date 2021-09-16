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
from dataclasses import dataclass
from typing import List, Optional

from django.utils.functional import cached_property


@dataclass
class LdapUserProfile:
    username: str
    display_name: str
    email: str
    telephone: str
    code: str

    departments: List[List[str]]

    @property
    def key_field(self):
        return self.username

    @property
    def display_str(self):
        return self.display_name


@dataclass
class LdapDepartment:
    name: str
    parent: Optional['LdapDepartment'] = None
    code: Optional[str] = None
    is_group: bool = False

    @property
    def key_field(self):
        return self.display_str

    @cached_property
    def display_str(self):
        if self.parent:
            return self.parent.display_str + "/" + self.name
        return self.name
