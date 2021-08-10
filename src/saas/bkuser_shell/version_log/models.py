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
import datetime
from typing import TYPE_CHECKING, Any, List

from pydantic import BaseModel, validator
from semantic_version import validate

from .constants import ProjectTypes, VersionDetailTypes


class ProjectDetail(BaseModel):
    type: VersionDetailTypes
    content: List[str] = []

    @validator("type")
    def type_validator(cls, v: str) -> str:
        if v is VersionDetailTypes:
            raise ValueError("版本日志详情类型错误")
        return v

    @validator("content", each_item=True)
    def content_validator(cls, v: str) -> str:
        if not v:
            raise ValueError("版本日志详情空错误")
        return v


class ChangeLog(BaseModel):
    """
    某个项目详情
    """

    project: ProjectTypes
    detail: List[ProjectDetail]

    @validator("project")
    def project_validator(cls, v: str) -> str:
        if v not in ProjectTypes.all():
            raise ValueError(f"不支持的项目: {v}")
        return v


class VersionLog(BaseModel):
    """
    版本日志模型
    """

    version: str
    date: str
    changeLogs: List[ChangeLog] = []

    @validator("version")
    def version_validator(cls, v: str) -> str:
        if not validate(v):
            raise ValueError("版本号格式错误")
        return v

    @validator("date")
    def date_validator(cls, v: str) -> str:
        try:
            return datetime.datetime.strptime(v, "%Y-%m-%d").strftime("%Y-%m-%d")
        except Exception:
            raise ValueError("日期格式错误，请遵循 %Y-%m-%d 格式填写")


class VersionLogSet(BaseModel):
    versions: List[VersionLog] = []
    __slots__ = ("_cache_number_map",)
    # there is a workaround for mypy's bug
    # https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        _cache_number_map: dict

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.versions.reverse()

        object.__setattr__(self, "_cache_number_map", {})
        for v in self.versions:
            self._cache_number_map[v.version] = v

    def get_by_version(self, version_number: str) -> VersionLog:
        try:
            return self.cache_map[version_number]
        except KeyError:
            raise ValueError(
                "Unknown version number: %s, please choose one of %s",
                version_number,
                list(self.cache_map.keys()),
            )

    @property
    def cache_map(self) -> dict:
        return self._cache_number_map
