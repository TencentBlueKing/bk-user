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

import bkuser_sdk
from bkuser_shell.bkiam.constants import ActionEnum
from bkuser_shell.common.viewset import BkUserApiViewSet
from django.utils.timezone import make_aware

from bkuser_global.drf_crown import ResponseParams, inject_serializer
from bkuser_global.utils import get_timezone_offset

from . import serializers
from .constants import OPERATION_OBJ_VALUE_MAP, OPERATION_VALUE_MAP

logger = logging.getLogger(__name__)


class AuditLogViewSet(BkUserApiViewSet):
    ACTION_ID = ActionEnum.VIEW_AUDIT.value

    def _get_categories_map(self, request) -> dict:
        """Get categories id map"""
        api_instance = bkuser_sdk.CategoriesApi(self.get_api_client_by_request(request, no_auth=True))
        categories = self.get_paging_results(api_instance.v2_categories_list)

        return {x["id"]: x for x in categories}

    @staticmethod
    def _get_request_params(validated_data: dict) -> dict:
        """Get params from validated_data"""

        # 前端传的是零时区时间，需要统一成当前时区的时间
        target_start_time = make_aware(validated_data["start_time"] + get_timezone_offset())
        target_end_time = make_aware(validated_data["end_time"] + get_timezone_offset())

        params = {
            "since": target_start_time,
            "until": target_end_time,
            "page": validated_data["page"],
            "page_size": validated_data["page_size"],
        }
        return params


class GeneralLogViewSet(AuditLogViewSet):
    @inject_serializer(
        query_in=serializers.GeneralLogListReqeustSerializer,
        out=serializers.OperationLogRespSLZ,
        tags=["audit"],
    )
    def list(self, request, validated_data: dict):
        categories = self._get_categories_map(request)
        api_instance = bkuser_sdk.AuditApi(self.get_api_client_by_request(request))

        params = self._get_request_params(validated_data)
        keyword = validated_data.get("keyword")
        if keyword:
            for m in [OPERATION_OBJ_VALUE_MAP, OPERATION_VALUE_MAP]:
                keyword = m.get(keyword, keyword)

            params.update(
                {
                    "wildcard_search": keyword.encode("unicode-escape"),
                    "wildcard_search_fields": ["extra_value", "operator"],
                }
            )

        return ResponseParams(
            api_instance.v2_audit_general_log_list(**params),
            {"context": {"categories": categories}},
        )


class LoginLogViewSet(AuditLogViewSet):
    @inject_serializer(
        query_in=serializers.LoginLogListReqeustSerializer,
        out=serializers.LoginLogRespSLZ,
        tags=["audit"],
    )
    def list(self, request, validated_data: dict):
        categories = self._get_categories_map(request)
        api_instance = bkuser_sdk.AuditApi(self.get_api_client_by_request(request))

        params = self._get_request_params(validated_data)
        return ResponseParams(api_instance.v2_audit_login_log_list(**params), {"context": {"categories": categories}})
