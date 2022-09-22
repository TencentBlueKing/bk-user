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
import logging

from rest_framework import generics, response

from bkuser_shell.common.error_codes import error_codes
from bkuser_shell.version_log.utils import get_version_list

logger = logging.getLogger(__name__)


class BKResponse(response.Response):
    @property
    def rendered_content(self):
        raw_data = self.data
        self.data = {"result": True, "code": 0, "message": "success", "data": raw_data}

        return super(BKResponse, self).rendered_content


class VersionLogListViewSet(generics.ListAPIView):
    permission_classes: list = []

    def list(self, request, *args, **kwargs):
        try:
            version_list = get_version_list()
            return BKResponse(data=version_list.dict())
        except ValueError:
            logger.exception("failed to parse release yaml")
            raise error_codes.VERSION_FORMAT_ERROR
