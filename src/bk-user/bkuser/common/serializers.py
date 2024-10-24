# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云-用户管理(Bk-User) available.
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
from typing import List

from django.utils.translation import gettext_lazy as _
from rest_framework import fields
from rest_framework.fields import empty


class StringArrayField(fields.CharField):
    """String representation of an array field"""

    default_error_messages = {
        "max_items": _("至多包含 {max_items} 个对象."),
        "min_items": _("至少包含 {min_items} 个对象."),
    }

    def __init__(self, min_items: int | None = None, max_items: int | None = None, delimiter: str = ",", **kwargs):
        self.min_items = min_items
        self.max_items = max_items
        self.delimiter = delimiter

        super().__init__(**kwargs)

    def run_validation(self, data=empty):
        data = super().run_validation(data)

        item_cnt = len(data)
        if self.min_items is not None and item_cnt < self.min_items:
            self.fail("min_items", min_items=self.min_items)

        if self.max_items is not None and item_cnt > self.max_items:
            self.fail("max_items", max_items=self.max_items)

        return data

    def to_internal_value(self, data) -> List[str]:
        # convert string to list
        data = super().to_internal_value(data)
        return [x.strip() for x in data.split(self.delimiter) if x]
