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
from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from rest_framework import status


class BkStandardResponseSwaggerAutoSchema(SwaggerAutoSchema):
    """定义了蓝鲸标准的响应格式，包括 data, error"""

    def get_response_schemas(self, response_serializers):
        responses = super().get_response_schemas(response_serializers)
        new_responses = OrderedDict()
        for sc, response in responses.items():
            # 失败情况
            if sc.isdigit() and status.is_success(int(sc)):
                # 成功
                data = self._get_successful_schema(response)
                properties = OrderedDict((("data", data),))
            else:
                properties = OrderedDict(
                    (("error", response.get("schema") or openapi.Schema(type=openapi.TYPE_OBJECT)),)
                )

            new_responses[sc] = openapi.Response(
                description=response.get("description", ""),
                schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties=properties),
            )

        # new_responses["40x/50x"] = openapi.Response(
        #     description="bk standard error",
        #     schema=openapi.Schema(
        #         type=openapi.TYPE_OBJECT,
        #         properties=OrderedDict((("error", self._get_bk_error_code_schema()),)),
        #     ),
        # )
        return new_responses

    def _get_successful_schema(self, response) -> openapi.Schema:
        """获取成功情况下的Schema"""
        # 无需分页，直接返回
        if not self.should_page():
            return response.get("schema") or openapi.Schema(type=openapi.TYPE_OBJECT)

        # 处理分页情况
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=OrderedDict(
                (
                    ("count", openapi.Schema(type=openapi.TYPE_INTEGER)),
                    ("results", response.get("schema")),
                )
            ),
            required=["count", "results"],
        )

    # @staticmethod
    # def _get_bk_error_code_schema() -> openapi.Schema:
    #     """基于蓝鲸Http API标准错误协议的错误码Schema"""
    #     return openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         properties=OrderedDict(
    #             (
    #                 (
    #                     "code",
    #                     openapi.Schema(type=openapi.TYPE_STRING, description="bk semantic error code category"),
    #                 ),
    #                 (
    #                     "message",
    #                     openapi.Schema(
    #                         type=openapi.TYPE_STRING, description="error message which should show to user"
    #                     ),
    #                 ),
    #                 (
    #                     "details",
    #                     openapi.Schema(
    #                         type=openapi.TYPE_ARRAY,
    #                         items=openapi.Schema(
    #                             type=openapi.TYPE_OBJECT,
    #                             properties=OrderedDict(
    #                                 (
    #                                     (
    #                                         "code",
    #                                         openapi.Schema(
    #                                             type=openapi.TYPE_STRING,
    #                                             description="current system semantic error code",
    #                                         ),
    #                                     ),
    #                                     (
    #                                         "message",
    #                                         openapi.Schema(
    #                                             type=openapi.TYPE_STRING,
    #                                             description="error message which should show to developer",
    #                                         ),
    #                                     ),
    #                                 )
    #                             ),
    #                         ),
    #                         description="error details for developer to troubleshoot or debug",
    #                     ),
    #                 ),
    #                 (
    #                     "data",
    #                     openapi.Schema(
    #                         type=openapi.TYPE_OBJECT,
    #                         description="used by the caller to perform some corresponding operations",
    #                     ),
    #                 ),
    #             )
    #         ),
    #     )
