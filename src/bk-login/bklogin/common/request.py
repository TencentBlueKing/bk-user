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
import json
from typing import Any, Dict

from django.utils.translation import gettext_lazy as _

from .error_codes import error_codes


def parse_request_body_json(body: bytes) -> Dict[str, Any]:
    try:
        request_body = json.loads(body.decode("utf-8"))
    except Exception as error:
        raise error_codes.INVALID_ARGUMENT.f(_("解析异常，Body 非 Json 格式数据, {}").format(error))

    return request_body
