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
from typing import Any, Dict, List, Optional

from django.http import JsonResponse


class APISuccessResponse(JsonResponse):
    """遵循蓝鲸Http API协议返回"""

    def __init__(self, data: Any = None, status: Optional[int] = None):
        wrapped_data = {"data": data}
        super(APISuccessResponse, self).__init__(wrapped_data, status=status)


class APIErrorResponse(JsonResponse):
    def __init__(
        self,
        code: str,
        message: str,
        system: str = "",
        details: Optional[List[Dict]] = None,
        data: Optional[Dict] = None,
        status: Optional[int] = None,
    ):
        wrapped_data = {
            "error": {
                "code": code,
                "message": message,
                "system": system,
                "details": details or [],
                "data": data or {},
            },
        }
        if status is None or (200 <= status < 300):  # noqa: PLR2004
            status = 400
        super(APIErrorResponse, self).__init__(wrapped_data, status=status)
