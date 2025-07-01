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

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.tenant.models import TenantUser


class MeVirtualUserListInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(help_text="搜索关键字", required=False, allow_blank=True, default="")


class MeVirtualUserOutputSLZ(serializers.Serializer):
    id = serializers.CharField(help_text="用户 ID")
    username = serializers.CharField(help_text="用户名")
    full_name = serializers.CharField(help_text="姓名")
    app_codes = serializers.ListField(child=serializers.CharField(), help_text="应用编码列表")
    owners = serializers.ListField(child=serializers.CharField(), help_text="责任人列表")
    created_at = serializers.DateTimeField(help_text="创建时间")


class MeVirtualUserRetrieveOutputSLZ(MeVirtualUserOutputSLZ):
    pass


class MeVirtualUserListOutputSLZ(MeVirtualUserOutputSLZ):
    pass


def _validate_owners(owners: List[str], tenant_id: str) -> List[str]:
    """
    校验责任人列表
    1. 检查每个责任人是否存在且为实体用户
    2. 检查每个责任人都应属于当前租户
    """
    valid_owners = set(
        TenantUser.objects.filter(
            id__in=owners, tenant_id=tenant_id, data_source__type=DataSourceTypeEnum.REAL
        ).values_list("id", flat=True)
    )
    if invalid_owners := set(owners) - valid_owners:
        raise ValidationError(_("用户 {} 不存在、不是实体用户或不属于当前租户").format(invalid_owners))

    return owners


class MeVirtualUserUpdateInputSLZ(serializers.Serializer):
    full_name = serializers.CharField(help_text="姓名")
    app_codes = serializers.ListField(help_text="应用编码列表", child=serializers.CharField())
    owners = serializers.ListField(help_text="责任人列表", child=serializers.CharField())

    def validate_app_codes(self, app_codes: List[str]) -> List[str]:
        # 过滤重复值
        return list(set(app_codes))

    def validate_owners(self, owners: List[str]) -> List[str]:
        tenant_id = self.context["tenant_id"]
        return _validate_owners(owners, tenant_id)
