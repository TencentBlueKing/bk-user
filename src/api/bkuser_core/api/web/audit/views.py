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

from django.db.models import Q
from rest_framework.generics import ListAPIView

from .constants import OPERATION_OBJ_VALUE_MAP, OPERATION_VALUE_MAP
from .serializers import (
    GeneralLogListRequestSerializer,
    GeneralLogSerializer,
    LoginLogListRequestSerializer,
    LoginLogSerializer,
)
from bkuser_core.api.web.utils import get_category_display_name_map
from bkuser_core.api.web.viewset import CustomPagination, StartTimeEndTimeFilterBackend
from bkuser_core.audit.models import GeneralLog, LogIn
from bkuser_core.bkiam.permissions import ViewAuditPermission


class GeneralLogListApi(ListAPIView):
    permission_classes = [ViewAuditPermission]
    pagination_class = CustomPagination
    serializer_class = GeneralLogSerializer

    filter_backends = [StartTimeEndTimeFilterBackend]

    def get_serializer_context(self):
        # set into context, for slz to_representation
        return self.get_serializer_context().update({'category_name_map': get_category_display_name_map()})

    def get_queryset(self):
        queryset = GeneralLog.objects.all()
        slz = GeneralLogListRequestSerializer(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # TODO: use drf Filter
        keyword = data.get("keyword")
        if keyword:
            # FIXME: 这里有问题,  操作人员/操作对象/操作类型 => 查询不准
            for m in [OPERATION_OBJ_VALUE_MAP, OPERATION_VALUE_MAP]:
                keyword = m.get(keyword, keyword)

            keyword = keyword.encode("unicode-escape")
            queryset = queryset.filter(Q(operator__icontains=keyword) | Q(extra_value__icontains=keyword))

        return queryset


class LoginLogListApi(ListAPIView):
    permission_classes = [ViewAuditPermission]
    pagination_class = CustomPagination
    serializer_class = LoginLogSerializer

    filter_backends = [StartTimeEndTimeFilterBackend]

    def get_queryset(self):
        queryset = LogIn.objects.all()
        slz = LoginLogListRequestSerializer(data=self.request.query_params)
        slz.is_valid(raise_exception=True)

        return queryset


# class LoginLogViewSet(AuditLogViewSet):
#     @inject_serializer(query_in=serializers.LoginLogListReqeustSerializer, tags=["audit"])
#     def export(self, request, validated_data: dict):
#         """导出登录日志"""
#         api_instance = bkuser_sdk.AuditApi(self.get_api_client_by_request(request))
#         profile_api_instance = bkuser_sdk.ProfilesApi(self.get_api_client_by_request(request))
#         fields_api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request))

#         params = self._get_request_params(validated_data)
#         login_logs = self.get_paging_results(
#             api_instance.v2_audit_login_log_list, since=params["since"], until=params["until"]
#         )
#         if not login_logs:
#             raise error_codes.CANNOT_EXPORT_EMPTY_LOG

#         fields = self.get_paging_results(fields_api_instance.v2_dynamic_fields_list)
#         fields.append(
#             bkuser_sdk.DynamicFields(name="create_time", display_name="登录时间", type="timer", order=0).to_dict()
#         )

#         exporter = ProfileExcelExporter(
#             load_workbook(settings.EXPORT_LOGIN_TEMPLATE), settings.EXPORT_EXCEL_FILENAME + "_login_audit", fields, 1
#         )

#         # TODO: remove step when #88 is done
#         step = 300
#         profile_ids = list({x["profile_id"] for x in login_logs})
#         profiles = []
#         counts = math.ceil(len(profile_ids) / step)
#         for _c in range(counts):
#             profiles.extend(
#                 self.get_paging_results(
#                     profile_api_instance.v2_profiles_list,
#                     lookup_field="id",
#                     exact_lookups=profile_ids[_c * step : (_c + 1) * step],
#                     include_disabled=True,
#                 )
#             )

#         extra_info = {x["profile_id"]: x for x in login_logs}
#         exporter.update_profiles(profiles, extra_info)

#         return exporter.to_response()
