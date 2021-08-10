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
from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import param_list_to_odict


class AutoModelTagSchema(SwaggerAutoSchema):
    def get_operation_id(self, operation_keys=None):
        if operation_keys[0] == "api":
            operation_keys = operation_keys[1:]

        return super().get_operation_id(operation_keys)

    def get_tags(self, operation_keys=None):
        operation_keys = operation_keys or self.operation_keys

        tags = self.overrides.get("tags")
        if tags:
            return tags

        if len(operation_keys) <= 1:
            return operation_keys

        if operation_keys[0] == "api":
            # v1 API 都放在一起不需要分类
            if operation_keys[1] == "v1":
                return [operation_keys[1]]
            elif operation_keys[1] == "v2":
                return [operation_keys[2]]

        return operation_keys

    def get_query_parameters(self):
        """Return the query parameters accepted by this view.

        :rtype: list[openapi.Parameter]
        """
        natural_parameters = self.get_filter_parameters() + self.get_pagination_parameters()

        query_serializer = self.get_query_serializer()
        serializer_parameters = []
        if query_serializer is not None:
            serializer_parameters = self.serializer_to_parameters(query_serializer, in_=openapi.IN_QUERY)

            # 如果用户已指定，则覆盖 natural_parameters
            natural_params_dict = param_list_to_odict(natural_parameters)
            for k, _ in param_list_to_odict(serializer_parameters).items():
                if k in natural_params_dict:
                    natural_parameters.remove(natural_params_dict[k])

        return natural_parameters + serializer_parameters
