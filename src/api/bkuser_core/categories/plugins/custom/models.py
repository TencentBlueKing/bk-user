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
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from django.db.models import Model

from .exceptions import NoKeyItemAvailable
from bkuser_core.departments.models import Department
from bkuser_core.profiles.models import Profile


@dataclass
class CustomType:
    # 不同于 DB 中的 pk，code 表示对象在外部系统中的唯一性
    __require_fields = ()
    __db_class = None
    __key_field = "code"
    __display_field = "display_name"

    def to_db_instance(self) -> Model:
        if not self.__db_class:
            raise NotImplementedError

        return self.__db_class()

    @classmethod
    def from_dict(cls, raw_dict: dict) -> "CustomType":
        return cls(**raw_dict)  # type: ignore

    @property
    def key_field(self) -> str:
        return self.__key_field

    @property
    def key(self) -> str:
        return getattr(self, self.key_field)

    @property
    def display_str(self) -> str:
        return getattr(self, self.__display_field)

    def __post_init__(self):
        for k in self.__require_fields:
            if not getattr(self, k):
                raise ValueError(f"{k} field is required.")


@dataclass
class CustomTypeList:
    items_map: Dict[Any, CustomType]

    def __len__(self):
        return len(self.items_map)

    def get(self, key: Any):
        try:
            return self.items_map[key]
        except KeyError:
            raise NoKeyItemAvailable(key)

    @classmethod
    def from_list(cls, items: List[CustomType]):
        items_map = {getattr(i, i.key_field): i for i in items}
        return cls(items_map=items_map)

    @property
    def values(self) -> list:
        return list(self.items_map.values())

    @property
    def custom_type(self) -> Type[CustomType]:
        return type(list(self.items_map.values())[0])


@dataclass
class CustomProfile(CustomType):
    """自定义的 Profile 对象"""

    __db_class = Profile
    # NOTE: 多渠道来源登录, email和telephone数据可能没有
    __require_fields = ("code", "username")

    code: str
    username: str

    email: Optional[str] = ""
    telephone: Optional[str] = ""
    display_name: Optional[str] = ""

    leaders: List[str] = field(default_factory=list)
    departments: List[str] = field(default_factory=list)

    extras: Optional[Dict] = field(default_factory=dict)
    position: Optional[str] = "0"


class CustomDepartment(CustomType):
    """自定义的 Department 对象"""

    __db_class = Department
    __display_field = "name"
    __require_fields = ("code", "name")

    code: str
    name: str
    parent: Optional[str] = ""

    def __init__(self, code, name, parent=None):
        self.code = code
        self.name = name
        self.parent = parent

    @property
    def display_str(self) -> str:
        return getattr(self, self.__display_field)
