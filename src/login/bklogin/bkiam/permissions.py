# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS
Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.conf import settings
from iam import Action, Request, Resource, Subject

from .base import new_iam


class Permission:
    def __init__(self):
        self._iam = new_iam()
        self._system_id = settings.BK_SYSTEM_ID_IN_IAM

    def _make_request_with_resources(self, username, action_id, resources):
        request = Request(
            self._system_id,
            Subject("user", username),
            Action(action_id),
            resources,
            None,
        )
        return request

    def allowed_access_app(self, username, app_code):
        """
        app访问权限
        """
        r = Resource(self._system_id, 'app', app_code, {})
        resources = [r]
        request = self._make_request_with_resources(username, "access_app", resources)
        return self._iam.is_allowed_with_cache(request)
