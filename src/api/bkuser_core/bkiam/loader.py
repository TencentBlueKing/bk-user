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

from django.conf import settings


@dataclass
class ConfigLoader:
    api_host: str
    iam_app_host: str
    system_id: str
    apply_path: str
    own_app_id: str = field(default="")
    own_app_token: str = field(default="")

    @classmethod
    def from_settings(cls) -> "ConfigLoader":
        return cls(**settings.IAM_CONFIG)

    @property
    def callback_url(self):
        return f"{self.iam_app_host}/{self.apply_path}"
