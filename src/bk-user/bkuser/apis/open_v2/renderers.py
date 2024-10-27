# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
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
from rest_framework import status
from rest_framework.renderers import JSONRenderer


class BkLegacyApiJSONRenderer(JSONRenderer):
    """蓝鲸历史版本 API Json 响应格式化"""

    format = "bk_legacy_json"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Wrap response data on demand
        resp = renderer_context["response"]
        if status.is_success(resp.status_code):
            data = {"result": True, "code": 0, "message": "", "data": data}
        elif status.is_client_error(resp.status_code) or status.is_server_error(resp.status_code):
            data = {"result": False, "code": -1, "message": data["message"], "data": {}}

        # For status codes other than (2xx, 4xx, 5xx), do not wrap data
        return super().render(data, accepted_media_type=None, renderer_context=None)
