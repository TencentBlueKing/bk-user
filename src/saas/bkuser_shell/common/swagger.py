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
from pydantic import BaseModel


class ExtraDefinitionsInspectorMixin:
    """把自定义Responses中的schema definition添加到全局的Definitions"""

    def get_response_serializers(self):
        overrides_responses = self.overrides.get("responses", None)
        if overrides_responses:
            for sc, resp in overrides_responses.items():
                if resp == {}:
                    continue

                # 判断是否继承自 BaseModel
                if issubclass(resp, BaseModel):
                    # 得益于 pydantic 原生支持 Swagger/OpenAPI 规范, 这里的类型转换完全兼容
                    schema = openapi.Schema(**resp.schema())
                    overrides_responses[sc] = schema
                    if "definitions" in schema:
                        # drf_yasg 目前只能获取 serializers 的 definitions
                        # 因此需要在这里补上 pydantic 的 definitions
                        self.components["definitions"].update(schema["definitions"])

        return super().get_response_serializers()


class BaseModelRequestBodyInspectorMixin:
    """将 swagger_auto_schema 中继承自 pydantic.BaseModel 的 request_body 转换成 drf_yasg.openapi.Schema"""

    def _get_request_body_override(self):
        body_override = self.overrides.get("request_body", None)
        # 判断是否继承自 BaseModel
        if body_override and issubclass(body_override, BaseModel):
            # 得益于 pydantic 原生支持 Swagger/OpenAPI 规范, 这里的类型转换完全兼容
            schema = openapi.Schema(**body_override.schema())
            if "definitions" in schema:
                # drf_yasg 目前只能获取 serializers 的 definitions
                # 因此需要在这里补上 pydantic 的 definitions
                self.components["definitions"].update(schema["definitions"])
            return schema

        return super()._get_request_body_override()


class ExtendedSwaggerAutoSchema(
    BaseModelRequestBodyInspectorMixin,
    ExtraDefinitionsInspectorMixin,
    SwaggerAutoSchema,
):
    """自定义的 schema 生成器"""
