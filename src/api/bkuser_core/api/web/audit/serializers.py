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
import datetime
from typing import Optional

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .constants import LOGIN_FAILED_REASON_MAP, OPERATION_ABOUT_PASSWORD, OPERATION_NAME_MAP, OPERATION_OBJ_NAME_MAP
from bkuser_core.profiles.models import Profile

PLACE_HOLDER = "--"


class LogListInputSLZ(serializers.Serializer):
    start_time = serializers.DateTimeField(input_formats=["iso-8601"], help_text=_("查询起始时间"))
    end_time = serializers.DateTimeField(input_formats=["iso-8601"], help_text=_("查询结束时间"))
    page = serializers.IntegerField(required=False, default=1, help_text=_("请求页码"))
    page_size = serializers.IntegerField(required=False, default=10, help_text=_("请求每页大小"))


class GeneralLogListInputSLZ(LogListInputSLZ):
    """General log list request"""

    keyword = serializers.CharField(required=False, help_text=_("搜索关键字"))


class GeneralLogOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text=_("ID"))
    extra_value = serializers.JSONField(help_text=_("额外信息"))
    display_name = serializers.CharField(help_text=_("用户全名"), read_only=True)
    operator = serializers.CharField(help_text=_("操作者"))
    create_time = serializers.DateTimeField(help_text=_("创建时间"))
    status = serializers.CharField(help_text=_("状态"))

    def to_representation(self, obj):
        # FIXME: use the SerializerMethodField instead of this
        instance = super().to_representation(obj)
        extra_value = instance["extra_value"]
        instance["target_obj"] = f"{extra_value['display_name']}<{extra_value['key']}>"
        instance["operation"] = (
            f"{OPERATION_NAME_MAP[extra_value['operation']]}"
            if extra_value["operation"] in OPERATION_ABOUT_PASSWORD
            else (
                f"{OPERATION_NAME_MAP[extra_value['operation']]}"
                f"-[{OPERATION_OBJ_NAME_MAP[extra_value.get('obj_type')]}]"
            )
        )

        category_name_map = self.context.get("category_name_map")

        category_id = extra_value.get("category_id")
        category_display_name = category_name_map.get(category_id, PLACE_HOLDER)
        operator_profile = Profile.objects.filter(username=obj.operator).first()
        display_name = operator_profile.display_name if operator_profile else ""

        return {
            "datetime": datetime.datetime.strptime(instance["create_time"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            "operator": instance["operator"],
            "target_obj": instance["target_obj"],
            "category_display_name": category_display_name,
            "display_name": display_name,
            "operation": instance["operation"],
            "client_ip": extra_value.get("client_ip", PLACE_HOLDER),
        }


class LoginLogListInputSLZ(LogListInputSLZ):
    """Login log list request"""

    is_success = serializers.BooleanField(required=False, allow_null=True, help_text=_("登录状态"))
    username = serializers.CharField(required=False, help_text=_("登录用户名"))


class LoginLogOutputSLZ(serializers.Serializer):
    # Tip: 使用source, 则不会走drf的 DATETIME_FORMAT 格式化
    # datetime = serializers.CharField(source="create_time", help_text=_("登录时间"), required=False)
    is_success = serializers.BooleanField(help_text=_("是否登录成功"), required=False)
    username = serializers.CharField(help_text=_("登录用户"), source="profile.username")
    display_name = serializers.CharField(help_text=_("用户全名"), source="profile.display_name")
    datetime = serializers.SerializerMethodField(help_text=_("登录时间"), required=False)
    category_display_name = serializers.SerializerMethodField(help_text=_("所属目录"), required=False)
    client_ip = serializers.SerializerMethodField(help_text=_("客户端 IP"), required=False)
    reason = serializers.SerializerMethodField(help_text=_("失败原因"), required=False)

    def get_datetime(self, obj):
        # 转换成本地时间
        local_time = timezone.localtime(obj.create_time)
        return local_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_reason(self, obj) -> Optional[str]:
        """get reason display name"""
        if obj.is_success:
            return None
        return LOGIN_FAILED_REASON_MAP.get(obj.reason, _("未知失败原因"))

    def get_category_display_name(self, obj) -> str:
        """get category display name from log extra value"""
        category_id = obj.profile.id
        category_name_map = self.context.get("category_name_map")
        category_display_name = category_name_map.get(category_id, PLACE_HOLDER)
        return category_display_name

    def get_client_ip(self, obj) -> str:
        """get client ip from extra_value"""
        if obj.extra_value:
            return obj.extra_value.get("client_ip", PLACE_HOLDER)
        return PLACE_HOLDER


class LoginLogExportOutputSLZ(serializers.Serializer):

    username = serializers.CharField(help_text=_("登录用户"), source="profile.username")
    display_name = serializers.CharField(help_text=_("登录用户名"), source="profile.display_name")
    ip = serializers.SerializerMethodField(help_text=_("客户端 IP"), required=False)
    status = serializers.SerializerMethodField(help_text=_("登录状态"), required=False)
    datetime = serializers.SerializerMethodField(help_text=_("登录时间"), required=False)
    reason = serializers.SerializerMethodField(help_text=_("失败原因"), required=False)

    def get_ip(self, obj) -> str:
        """get client ip from extra_value"""
        if obj.extra_value:
            return obj.extra_value.get("client_ip", PLACE_HOLDER)
        return PLACE_HOLDER

    def get_status(self, obj) -> str:
        # bugfix: ugettext_lazy for excel export
        if obj.is_success:
            return str(_("成功"))
        return str(_("失败"))

    def get_reason(self, obj) -> Optional[str]:
        """get reason display name"""
        if obj.is_success:
            return None
        # bugfix: ugettext_lazy
        return str(LOGIN_FAILED_REASON_MAP.get(obj.reason, _("未知失败原因")))

    def get_datetime(self, obj):
        return obj.create_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
