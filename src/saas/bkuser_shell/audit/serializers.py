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

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .constants import LOGIN_FAILED_REASON_MAP, OPERATION_ABOUT_PASSWORD, OPERATION_NAME_MAP, OPERATION_OBJ_NAME_MAP

PLACE_HOLDER = "--"


# --------------- In -----------------
class LogRequestSerializer(serializers.Serializer):
    start_time = serializers.DateTimeField(input_formats=["iso-8601"], help_text=_("查询起始时间"))
    end_time = serializers.DateTimeField(input_formats=["iso-8601"], help_text=_("查询结束时间"))
    page = serializers.IntegerField(required=False, default=1, help_text=_("请求页码"))
    page_size = serializers.IntegerField(required=False, default=10, help_text=_("请求每页大小"))


class LoginLogListReqeustSerializer(LogRequestSerializer):
    """Login log list request"""


# --------------- Out -----------------
class OperationLogListSerializer(serializers.Serializer):
    datetime = serializers.DateTimeField(read_only=True)
    operator = serializers.CharField(read_only=True)
    target_obj = serializers.CharField(read_only=True, help_text=_("操作对象"))
    operation = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        extra_value = instance["extra_value"]
        categories = self.context.get("categories")
        instance["target_obj"] = f"{extra_value['display_name']}<{extra_value['key']}>"
        instance["operation"] = (
            f"{OPERATION_NAME_MAP[extra_value['operation']]}"
            if extra_value['operation'] in OPERATION_ABOUT_PASSWORD
            else (
                f"{OPERATION_NAME_MAP[extra_value['operation']]}"
                f"{OPERATION_OBJ_NAME_MAP[extra_value.get('obj_type')]}"
            )
        )

        category_id = extra_value.get("category_id")
        if category_id and categories.get(category_id):
            category_display_name = categories.get(category_id).get("display_name", _("_该目录已被删除_"))
        else:
            category_display_name = PLACE_HOLDER

        return {
            "datetime": datetime.datetime.strptime(instance["create_time"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            "operator": instance["operator"],
            "target_obj": instance["target_obj"],
            "category_display_name": category_display_name,
            "operation": instance["operation"],
            "client_ip": extra_value.get("client_ip", PLACE_HOLDER),
        }


class LoginLogListSerializer(serializers.Serializer):
    """Login log list response slz"""

    datetime = serializers.CharField(source="create_time", help_text=_("登录时间"), required=False)
    is_success = serializers.BooleanField(help_text=_("是否登录成功"), required=False)
    username = serializers.CharField(help_text=_("用户名"), required=False)
    category_display_name = serializers.SerializerMethodField(help_text=_("所属目录"), required=False)
    client_ip = serializers.SerializerMethodField(help_text=_("客户端 IP"), required=False)
    reason = serializers.SerializerMethodField(help_text=_("失败原因"), required=False)

    def get_reason(self, obj: dict) -> Optional[str]:
        """get reason display name"""
        if obj["is_success"]:
            return None
        return LOGIN_FAILED_REASON_MAP.get(obj["reason"], _("未知失败原因"))

    def get_category_display_name(self, obj: dict) -> str:
        """get category display name from log extra value"""
        category_id = int(obj["category_id"])
        categories = self.context.get("categories")

        if category_id and categories.get(category_id):
            category_display_name = categories.get(category_id).get("display_name", _("_该目录已被删除_"))
        else:
            category_display_name = PLACE_HOLDER

        return category_display_name

    def get_client_ip(self, obj: dict) -> str:
        """get client ip from extra_value"""
        client_ip = PLACE_HOLDER
        if obj["extra_value"]:
            client_ip = obj["extra_value"].get("client_ip", PLACE_HOLDER)

        return client_ip


class LoginLogRespSLZ(serializers.Serializer):
    count = serializers.IntegerField()
    results = LoginLogListSerializer(many=True)
