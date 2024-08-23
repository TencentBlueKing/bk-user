# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from rest_framework import serializers

from bkuser.common.constants import TIME_ZONE_CHOICES


class ProfileUpdateInputSLZ(serializers.Serializer):
    username = serializers.CharField(help_text="用户名")
    # Note: 只兼容允许修改 language、time_zone、wx_userid 字段
    # display_name = serializers.CharField(help_text="姓名", required=False)
    # telephone = serializers.CharField(
    #     help_text="手机号，仅支持中国大陆",
    #     required=False,
    #     min_length=11,
    #     max_length=11,
    # )
    # email = serializers.EmailField(help_text="邮箱", required=False)
    language = serializers.ChoiceField(help_text="语言", required=False, choices=["zh-cn", "en"])
    time_zone = serializers.ChoiceField(help_text="时区", required=False, choices=TIME_ZONE_CHOICES)
    wx_userid = serializers.CharField(help_text="绑定的微信消息通知的账号 ID", required=False, allow_blank=True)


class ProfileBatchQueryInputSLZ(serializers.Serializer):
    username_list = serializers.ListField(child=serializers.CharField(help_text="用户名"), max_length=100)
