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
from .serializers import (
    GeneralLogListInputSLZ,
    GeneralLogOutputSLZ,
    LoginLogExportOutputSLZ,
    LoginLogListInputSLZ,
    LoginLogOutputSLZ,
)
from bkuser_core.api.web.export import LoginLogExcelExporter
from bkuser_core.api.web.utils import get_category_display_name_map
from bkuser_core.api.web.viewset import CustomPagination, StartTimeEndTimeFilterBackend
from bkuser_core.audit.models import GeneralLog, LogIn
from bkuser_core.bkiam.permissions import ViewAuditPermission
from bkuser_core.common.error_codes import error_codes

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
            # 注意, GeneralLogOutputSLZ 展示在表格里的字段格式是: 更新-[用户] to 更新 to `update`
            # 用户可能复制后粘贴搜索: 更新-[用户] to 更新 to `update`
            keyword = keyword.split("-")[0]
            for m in [OPERATION_OBJ_VALUE_MAP, OPERATION_VALUE_MAP]:
                keyword = m.get(keyword, keyword)

            queryset = queryset.filter(Q(operator__icontains=keyword) | Q(extra_value__icontains=keyword))

        return queryset


class LoginLogSearchQuerySetMinix:
    def get_queryset(self):
        queryset = LogIn.objects.all()
        slz = LoginLogListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # TODO: use drf Filter
        # Note: is_success为bool类型，经过Drf SLZ后有4种情况：（1）不存在（2）None（allow_null=True）（3）True（4）False
        #  当前场景下，不存在或None，则表示可以查询所有状态的记录
        is_success = data.get("is_success")
        if is_success is not None and "is_success" in self.request.query_params:
            logger.debug("login_in filter: is_success:<{}>".format(is_success))
            queryset = queryset.filter(is_success=is_success)

        username = data.get("username")
        if username:
            logger.debug("login_in filter: username:<{}>".format(username))
            queryset = queryset.filter(profile__username__icontains=username)

        return queryset


class LoginLogListApi(LoginLogSearchQuerySetMinix, generics.ListAPIView):
    permission_classes = [ViewAuditPermission]
    pagination_class = CustomPagination
    serializer_class = LoginLogOutputSLZ
    filter_backends = [StartTimeEndTimeFilterBackend]

    def get_serializer_context(self):
        # set into context, for slz to_representation
        return {"category_name_map": get_category_display_name_map()}


class LoginLogExportApi(LoginLogSearchQuerySetMinix, generics.ListAPIView):
    permission_classes = [ViewAuditPermission]
    # 登录审计日志导出 不需要分页
    # pagination_class = CustomPagination

    filter_backends = [StartTimeEndTimeFilterBackend]

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
        exporter = LoginLogExcelExporter(
            load_workbook(settings.EXPORT_LOGIN_TEMPLATE),
            settings.EXPORT_EXCEL_FILENAME + "_login_audit",
        )

        login_logs = queryset.all()
        records = []
        for login_log in login_logs:
            record = LoginLogExportOutputSLZ(login_log, context=self.get_serializer_context()).data
            records.append(record)

        exporter.add_records(records)
        return exporter.to_response()
