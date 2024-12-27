# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from typing import List

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.tenant.constants import TenantStatus


class TenantListOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="租户 ID")
    name = serializers.CharField(help_text="租户名")
    status = serializers.ChoiceField(help_text="租户状态", choices=TenantStatus.get_choices())

    class Meta:
        ref_name = "open_v3.TenantListOutputSLZ"


class TenantUserDisplayNameListInputSLZ(serializers.Serializer):
    bk_usernames = serializers.CharField(help_text="蓝鲸唯一标识，多个用逗号分隔")

    def validate_bk_usernames(self, bk_usernames: str) -> List[str]:
        # 判断个数
        if len(bk_usernames.split(",")) > settings.BK_USERNAME_BATCH_QUERY_DISPLAY_NAME_LIMIT:
            raise ValidationError(
                _("待查询的 bk_username 个数不能超过 %s") % settings.BK_USERNAME_BATCH_QUERY_DISPLAY_NAME_LIMIT
            )

        return bk_usernames.split(",")

    class Meta:
        ref_name = "open_v3.DisplayNameListInputSLZ"


class TenantUserDisplayNameListOutputSLZ(serializers.Serializer):
    bk_username = serializers.CharField(help_text="用户名", source="id")
    display_name = serializers.CharField(help_text="用户展示名称", source="data_source_user.full_name")

    class Meta:
        ref_name = "open_v3.DisplayNameListOutputSLZ"
