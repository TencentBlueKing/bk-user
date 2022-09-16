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

from django.conf import settings
from django.db.models import Q
from openpyxl import load_workbook
from rest_framework import generics

from .constants import OPERATION_OBJ_VALUE_MAP, OPERATION_VALUE_MAP
from .serializers import GeneralLogListInputSLZ, GeneralLogOutputSLZ, LoginLogListRequestSerializer, LoginLogSerializer
from bkuser_core.api.web.category.serializers import CategoryExportProfileSerializer
from bkuser_core.api.web.export import ProfileExcelExporter
from bkuser_core.api.web.field.serializers import FieldSerializer
from bkuser_core.api.web.utils import get_category_display_name_map
from bkuser_core.api.web.viewset import CustomPagination, StartTimeEndTimeFilterBackend
from bkuser_core.audit.models import GeneralLog, LogIn
from bkuser_core.bkiam.permissions import ViewAuditPermission
from bkuser_core.common.error_codes import error_codes
from bkuser_core.profiles.models import DynamicFieldInfo

logger = logging.getLogger(__name__)


class GeneralLogListApi(generics.ListAPIView):
    permission_classes = [ViewAuditPermission]
    pagination_class = CustomPagination
    serializer_class = GeneralLogOutputSLZ

    filter_backends = [StartTimeEndTimeFilterBackend]

    def get_serializer_context(self):
        # set into context, for slz to_representation
        return {"category_name_map": get_category_display_name_map()}

    def get_queryset(self):
        queryset = GeneralLog.objects.all()
        slz = GeneralLogListInputSLZ(data=self.request.query_params)
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


class LoginLogListApi(generics.ListAPIView):
    permission_classes = [ViewAuditPermission]
    pagination_class = CustomPagination
    serializer_class = LoginLogSerializer

    filter_backends = [StartTimeEndTimeFilterBackend]

    def get_serializer_context(self):
        # set into context, for slz to_representation
        return {"category_name_map": get_category_display_name_map()}

    def get_queryset(self):
        queryset = LogIn.objects.all()
        slz = LoginLogListRequestSerializer(data=self.request.query_params)
        slz.is_valid(raise_exception=True)

        return queryset


class LoginLogExportApi(generics.ListAPIView):
    permission_classes = [ViewAuditPermission]
    # 登录审计日志导出 不需要分页
    # pagination_class = CustomPagination

    filter_backends = [StartTimeEndTimeFilterBackend]

    def get_queryset(self):
        queryset = LogIn.objects.all()
        slz = LoginLogListRequestSerializer(data=self.request.query_params)
        slz.is_valid(raise_exception=True)

        return queryset

    def get(self, request, *args, **kwargs):
        """导出登录日志"""
        queryset = self.filter_queryset(self.get_queryset())

        # 计算长度
        count = queryset.count()
        if count == 0:
            raise error_codes.CANNOT_EXPORT_EMPTY_LOG
        if count > 10000:
            logger.warning("login log too large, only export top 10000")
            queryset = queryset[:10000]

        # 提前获取用户
        queryset.select_related("profile")

        fields = DynamicFieldInfo.objects.filter(enabled=True).all()
        fields_data = FieldSerializer(fields, many=True).data
        fields_data.append(
            {
                "id": len(fields_data) + 1,
                "key": "datetime",
                "name": "登录时间",
                "options": [],
                "display_name": "登录时间",
                "type": "timer",
                "require": True,
                "unique": True,
                "editable": True,
                "configurable": True,
                "builtin": False,
                "order": 0,
                "default": "",
                "enabled": True,
                "visible": True,
            },
        )
        # TODO: 应该改造, 使用原生的登录审计: 用户-登录时间-来源 IP-登录状态-失败原因等等
        # 可能再补充一些额外信息, 但是不应该导出profiles的信息

        exporter = ProfileExcelExporter(
            load_workbook(settings.EXPORT_LOGIN_TEMPLATE),
            settings.EXPORT_EXCEL_FILENAME + "_login_audit",
            fields_data,
            1,
        )

        context = {"category_name_map": get_category_display_name_map()}
        login_logs = queryset.all()

        profiles = [x.profile for x in login_logs]
        all_profiles = CategoryExportProfileSerializer(profiles, many=True).data

        # FIXME: bug here, 这里的key是profile.id, 会导致每个用户只有一条登录审计记录 => 这是有问题的
        extra_info = {x.profile.id: LoginLogSerializer(x, context=context).data for x in login_logs}
        exporter.update_profiles(all_profiles, extra_info)

        return exporter.to_response()
