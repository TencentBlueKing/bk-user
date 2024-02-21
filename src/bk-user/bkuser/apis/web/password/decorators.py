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

import wrapt
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def handle_exception_with_settings():
    """适用于 Django View 方法的装饰器，用于密码重置相关 api，根据 settings 配置判断是否返回异常信息"""

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        try:
            return wrapped(*args, **kwargs)
        except Exception:
            if settings.ALLOW_RAISE_ERROR_TO_USER_WHEN_RESET_PASSWORD:
                raise

            logger.exception("exception in user reset password api...")
            return Response(status=status.HTTP_204_NO_CONTENT)

    return wrapper
