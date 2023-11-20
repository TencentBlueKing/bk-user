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
from typing import List

from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel, model_validator


class Option(BaseModel):
    id: str
    value: str

    @model_validator(mode="after")
    def validate_attrs(self) -> "Option":
        if not self.id or not self.value:
            raise ValueError(_("枚举ID或枚举不可为空"))

        return self


class TenantUserCustomFieldOptions(BaseModel):
    """用户自定义字段-options字段"""

    options: List[Option]
