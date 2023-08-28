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
import pytest
from bkuser.utils.pydantic import stringify_pydantic_error
from pydantic import BaseModel, Field, ValidationError, model_validator


@pytest.mark.parametrize(
    ("foo", "bar", "err_msg"),
    [
        (9, 10, "foo: Input should be greater than 10, bar: Input should be less than 10"),
        (11, 10, "bar: Input should be less than 10"),
        # 由于 Field 的校验提前异常，不会触发 validate_attrs 的校验
        (12, 10, "bar: Input should be less than 10"),
        (12, 8, "foo can't be even"),
        (11, 9, "bar can't be odd"),
    ],
)
def test_stringify_pydantic_error(foo, bar, err_msg):
    class TModel(BaseModel):
        foo: int = Field(gt=10)
        bar: int = Field(lt=10)

        @model_validator(mode="after")
        def validate_attrs(self):
            if not self.foo & 1:
                raise ValueError("foo can't be even")

            if self.bar & 1:
                raise ValueError("bar can't be odd")

            return self

    try:
        TModel(foo=foo, bar=bar)
    except ValidationError as e:
        assert stringify_pydantic_error(e) == err_msg  # noqa: PT017
