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
import functools
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional, Type, Union

from django.conf import settings
from django.http.response import HttpResponseBase
from django.utils.module_loading import import_string
from rest_framework import status
from rest_framework.fields import empty
from rest_framework.serializers import BaseSerializer

from .options import WearOptions
from .out import ResponseParams

try:
    from drf_yasg.utils import swagger_auto_schema

except ImportError:
    WearOptions.skip_swagger_schema = True

if TYPE_CHECKING:
    from rest_framework.request import Request

_DEFAULT_SETTINGS_PREFIX = "DRF_CROWN_"


def enable_unittest():
    """Call me when you running testing"""
    WearOptions.is_unittest = True


@dataclass
class Config:
    """Config for Injector, control the process of injecting"""

    return_validated_data: bool = True
    remain_request: bool = False
    # sometime return raw data instead of serializer
    skip_out_cls: bool = False
    default_return_status: status = status.HTTP_200_OK


@dataclass
class ViewCrown:
    """A injector for injecting serializer as dependency"""

    body_in: Optional[Union[Type[BaseSerializer], BaseSerializer]]
    query_in: Optional[Union[Type[BaseSerializer], BaseSerializer]]
    out: Union[Type[BaseSerializer], BaseSerializer]
    config_params: dict = field(default_factory=dict)
    valid_params: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.query_in and self.body_in:
            raise ValueError("there should be only one param between in_body & in_query")

        self.valid_params = self.valid_params or {"raise_exception": True}

        # Priority decreases
        # 1. config as parameter from decorator
        # 2. config from django.settings
        # 3. config from Config class(above)
        _config = getattr(settings, _DEFAULT_SETTINGS_PREFIX + "DEFAULT_CONFIG", {}).copy()
        _config.update(self.config_params or {})
        self.config = Config(**_config)

        # remain an entrance for custom response class
        try:
            self.resp_cls = import_string(getattr(settings, _DEFAULT_SETTINGS_PREFIX + "RESP_CLS"))
        except AttributeError:
            self.resp_cls = import_string("rest_framework.response.Response")

    def get_in_serializer_instance(self, request: Optional["Request"] = None) -> "BaseSerializer":
        if not self.body_in and not self.query_in:
            raise ValueError("should given at least one serializer input")

        _data = empty
        if self.body_in:
            _in = self.body_in

            if request is not None:
                _data = getattr(request, "data")
        else:
            _in = self.query_in

            if request is not None:
                _data = getattr(request, "query_params")

        if isinstance(_in, BaseSerializer):
            _in.initial_data = _data
            slz_obj = _in
        elif issubclass(_in, BaseSerializer):
            slz_obj = _in(data=_data)
        else:
            raise ValueError("unknown serializer input")

        return slz_obj

    def get_serializer_instance_by_request(self, request: "Request") -> "BaseSerializer":
        """Get in serializer instance"""
        slz_obj = self.get_in_serializer_instance(request)
        slz_obj.is_valid(**self.valid_params)
        return slz_obj

    def get_validated_data(self, request: "Request") -> dict:
        """Get validated data via in_serializer"""
        return self.get_serializer_instance_by_request(request).validated_data

    def get_in_params(self, request: "Request") -> dict:
        """Get extra params before view logic"""
        if WearOptions.is_unittest:
            return {}

        if self.config.return_validated_data:
            return {"validated_data": self.get_validated_data(request)}
        else:
            return {"serializer_instance": self.get_serializer_instance_by_request(request)}

    def get_response(self, data, out_params: dict) -> Any:
        """Get Response data"""
        if WearOptions.is_unittest:
            return data

        if self.config.skip_out_cls:
            return data

        if isinstance(data, (self.resp_cls, HttpResponseBase)):
            return data

        if isinstance(self.out, BaseSerializer):
            # 由于传入的是全局对象，会残留上一次请求的结果
            # 这里需要手动清理一下
            if hasattr(self.out, "_data"):
                delattr(self.out, "_data")

            self.out.instance = data
            _data = self.out.data
        elif issubclass(self.out, BaseSerializer):
            _data = self.out(data, **out_params).data
        else:
            raise ValueError("unknown serializer output")

        return self.resp_cls(data=_data, status=self.config.default_return_status)


def generate_swagger_params(crown: ViewCrown, swagger_params: dict) -> dict:
    """
    assemble params for swagger_auto_schema by crown
    """
    default_params = {}
    if crown.body_in:
        default_params = {"request_body": crown.get_in_serializer_instance()}
    elif crown.query_in:
        default_params = {"query_serializer": crown.get_in_serializer_instance()}

    if crown.out:
        default_params.update({"responses": {crown.config.default_return_status: crown.out}})

    default_params.update(swagger_params or {})
    return default_params


def inject_serializer(
    body_in: Optional[Union[Type[BaseSerializer], BaseSerializer]] = None,
    query_in: Optional[Union[Type[BaseSerializer], BaseSerializer]] = None,
    out: Optional[Union[Type[BaseSerializer], BaseSerializer]] = None,
    config: Optional[dict] = None,
    **swagger_kwargs
):
    """
    Sugar for simpling drf serializer specification
    :param body_in: input serializer (request body)
    :param query_in: input serializer (query)
    :param out: output serializer
    :param config: initial info of Config
    :param swagger_kwargs: pass to swagger_auto_schema of drf-yasg
    """

    def decorator_serializer_inject(func):
        crown = ViewCrown(body_in, query_in, out, config)

        if not WearOptions.skip_swagger_schema:
            func = swagger_auto_schema(**generate_swagger_params(crown, swagger_kwargs))(func)

        @functools.wraps(func)
        def decorated(*args, **kwargs):
            args = list(args)
            in_content = {}
            if body_in or query_in:
                in_content.update(**crown.get_in_params(args[1]))

            if not crown.config.remain_request:
                del args[1]

            original_data = func(*args, **kwargs, **in_content)
            if not out:
                return original_data

            # support runtime serializer params, like "context"
            params = {}
            if isinstance(original_data, ResponseParams):
                params = original_data.params
                original_data = original_data.data

            return crown.get_response(original_data, params)

        return decorated

    return decorator_serializer_inject
