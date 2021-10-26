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
from typing import TYPE_CHECKING, Any, Dict, Optional

from django.conf import settings

from ..common.error_codes import CoreAPIError
from . import models
from .constants import OperationEnum, OperationStatusEnum
from .models import GeneralLog, ProfileRelatedLog

if TYPE_CHECKING:
    from bkuser_core.profiles.models import Profile
    from rest_framework.request import Request

logger = logging.getLogger(__name__)


def get_client_ip(request: "Request") -> str:
    # prior to use client ip from saas
    client_ip_from_saas = request.META.get(settings.CLIENT_IP_FROM_SAAS_HEADER)
    if client_ip_from_saas:
        return client_ip_from_saas

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        for h in ["REMOTE_ADDR", "X-Real-IP"]:
            ip = request.META.get(h)
            if ip:
                break

    return ip


def create_general_log(
    operator: str,
    operate_type: str,
    operator_obj: Any,
    status: str = OperationStatusEnum.SUCCEED.value,
    extra_info: Dict = None,
    request=None,
) -> Optional[GeneralLog]:
    """记录操作日志 快捷函数"""
    try:
        audit_info = operator_obj.to_audit_info()
    except AttributeError:
        logger.exception("Object<%s> should add to_audit_info() method", operator_obj.__class__)
        return None

    if not OperationEnum.has_value(operate_type):
        logger.exception("operate type<%s> unknown", operate_type)
        return None

    extra_value = {
        "operation": operate_type,
        "obj_type": operator_obj.__class__.__name__,
    }
    if request:
        extra_value["client_ip"] = get_client_ip(request)

    extra_value.update(audit_info.to_dict())
    extra_value.update(extra_info or {})

    logger.info(
        "Operator<%s> %s object<%s> of %s",
        operator,
        operate_type,
        operator_obj,
        operator_obj.__class__.__name__,
    )
    return GeneralLog.objects.create(operator=operator, extra_value=extra_value, status=status)


def create_profile_log(
    profile: "Profile", operation: str, params: dict = None, request: "Request" = None
) -> ProfileRelatedLog:
    create_params = params or {}
    if request:
        create_params.update({"extra_value": {"client_ip": get_client_ip(request)}})

    try:
        return getattr(models, operation).objects.create(profile=profile, **create_params)
    except AttributeError:
        raise ValueError("unknown operation for profile log")
    except Exception:
        raise ValueError("operation is not a profile log type")


def audit_error_general_log(operate_type):
    """定义捕获异常的审计日志装饰器"""

    def catch_exc(func):
        def _catch_exc(self, request, *args, **kwargs):
            try:
                func(self, request, *args, **kwargs)

            except CoreAPIError as e:
                create_general_log(
                    operator=request.operator,
                    operate_type=operate_type,
                    operator_obj=self.get_object(),
                    request=request,
                    status=OperationStatusEnum.FAILED.value,
                    extra_info={"failed_info": f"{e.message}"},
                )
                return

        return _catch_exc

    return catch_exc
