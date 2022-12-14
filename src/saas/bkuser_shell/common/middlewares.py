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
import copy
import json
import logging

from django.utils.deprecation import MiddlewareMixin

from bkuser_shell.common.utils import escape_name

logger = logging.getLogger(__name__)


class CheckXssMiddleware(MiddlewareMixin):
    def __init__(self, *args, **kwargs):
        self.__escape_param_list = []
        super(CheckXssMiddleware, self).__init__(*args, **kwargs)

    def process_view(self, request, view, args, kwargs):
        try:
            if request.method in ["POST", "PUT", "PATCH"]:
                json_data = json.loads(request.body)
                escape_data = json.dumps(self.__escape_data(json_data))
                request._body = escape_data.encode()
        except Exception as err:  # pylint: disable=broad-except
            logger.error(u"CheckXssMiddleware 转换失败！%s" % err)
        return None

    def _transfer(self, _get_value):
        if isinstance(_get_value, list):
            return [escape_name(_value) for _value in _get_value if isinstance(_value, str)]
        elif isinstance(_get_value, dict):
            return _get_value
        else:
            return escape_name(_get_value)

    def __escape_data(self, data):
        """
        参数转义
        """
        data_copy = copy.deepcopy(data)
        # 豁免list, SaaS接口传入参数为list类型，一般为目录设置部分，豁免这部分接口参数转义
        if isinstance(data, list):
            return data_copy

        for _get_key, _get_value in data.items():
            data_copy[_get_key] = self._transfer(_get_value)

        return data_copy
