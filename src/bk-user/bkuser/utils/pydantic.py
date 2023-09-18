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
from typing import Type

import jsonref
from drf_yasg import openapi
from pydantic import BaseModel, ValidationError


def stringify_pydantic_error(exc: ValidationError) -> str:
    """Transform a pydantic Exception object to a one-line string"""

    err_msgs = []
    for err in exc.errors():
        # Note: 裁剪掉不必要的 `Value error, ` 前缀
        msg = err["msg"].removeprefix("Value error, ")

        loc_msg = " -> ".join([str(i) for i in err["loc"]])
        if loc_msg:
            msg = f"{loc_msg}: {msg}"

        err_msgs.append(msg)

    return ", ".join(err_msgs)


def gen_openapi_schema(model: Type[BaseModel]) -> openapi.Schema:
    """Convert pydantic model as drf_yasg openapi schema (without any jsonRef)"""
    # Q: why need json dumps and jsonref.loads?
    # A: according to https://github.com/pydantic/pydantic/issues/889
    #    pydantic generate json schema with jsonRef,
    #    which is not compatible with drf_yasg.openapi.schema
    json_schema = jsonref.loads(json.dumps(model.model_json_schema()))
    return openapi.Schema(**json_schema)
