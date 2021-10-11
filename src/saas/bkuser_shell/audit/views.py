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
import math

import bkuser_sdk
from bkuser_shell.audit import serializers
from bkuser_shell.audit.constants import OPERATION_OBJ_VALUE_MAP, OPERATION_VALUE_MAP
from bkuser_shell.bkiam.constants import ActionEnum
from bkuser_shell.common.error_codes import error_codes
from bkuser_shell.common.export import ProfileExcelExporter
from bkuser_shell.common.viewset import BkUserApiViewSet
from django.conf import settings
from django.utils.timezone import make_aware
from openpyxl import load_workbook

from bkuser_global.drf_crown import ResponseParams, inject_serializer
from bkuser_global.utils import get_timezone_offset

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

    @inject_serializer(query_in=serializers.LoginLogListReqeustSerializer, tags=["audit"])
    def export(self, request, validated_data: dict):
        """导出登录日志"""
        api_instance = bkuser_sdk.AuditApi(self.get_api_client_by_request(request))
        profile_api_instance = bkuser_sdk.ProfilesApi(self.get_api_client_by_request(request))
        fields_api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request))

        params = self._get_request_params(validated_data)
        login_logs = self.get_paging_results(
            api_instance.v2_audit_login_log_list, since=params["since"], until=params["until"]
        )
        if not login_logs:
            raise error_codes.CANNOT_EXPORT_EMPTY_LOG

        fields = self.get_paging_results(fields_api_instance.v2_dynamic_fields_list)
        fields.append(
            bkuser_sdk.DynamicFields(name="create_time", display_name="登录时间", type="timer", order=0).to_dict()
        )

        exporter = ProfileExcelExporter(
            load_workbook(settings.EXPORT_LOGIN_TEMPLATE), settings.EXPORT_EXCEL_FILENAME, fields, 1
        )

        # TODO: remove step when #88 is done
        step = 300
        profile_ids = list({x["profile_id"] for x in login_logs})
        profiles = []
        counts = math.ceil(len(profile_ids) / step)
        for _c in range(counts):
            profiles.extend(
                self.get_paging_results(
                    profile_api_instance.v2_profiles_list,
                    lookup_field="id",
                    exact_lookups=profile_ids[_c * step : (_c + 1) * step],
                    include_disabled=True,
                )
            )

        extra_info = {x["profile_id"]: x for x in login_logs}
        exporter.update_profiles(profiles, extra_info)

        return exporter.to_response()
