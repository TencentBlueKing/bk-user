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
from rest_framework import status
from rest_framework.renderers import JSONRenderer


class BkStandardApiJSONRenderer(JSONRenderer):
    """Renderer which wraps original JSON response with an extra layer.

    Normal
    - Original: `{"foo": [1, 2]}`
    - Wrapped: `{"data": {"foo": [1, 2]}}`

    Error
    - Original: `{"code": "xxxx",...}`
    - Wrapped: `{"error": {"code": "xxxx",...}}`
    """

    format = "bk_std_json"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Wrap response data on demand
        resp = renderer_context["response"]
        if status.is_success(resp.status_code):
            data = {"data": data}
        elif status.is_client_error(resp.status_code) or status.is_server_error(resp.status_code):
            data = {"error": data}
        # For status codes other than (2xx, 4xx, 5xx), do not wrap data
        return super().render(data, accepted_media_type=None, renderer_context=None)
