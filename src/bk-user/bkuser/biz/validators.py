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
import re

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

TENANT_ID_REGEX = r"^([a-zA-Z])([a-zA-Z0-9.-]){2,31}"


def validate_tenant_id(value):
    if not re.fullmatch(re.compile(TENANT_ID_REGEX), value):
        raise ValidationError(_("{} 不符合 租户ID 的命名规范: 由3-32位字母、数字、点(.)、连接符(-)字符组成，以字母开头").format(value))  # noqa: E501
