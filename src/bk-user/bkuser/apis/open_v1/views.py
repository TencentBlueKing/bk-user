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

import phonenumbers
from django.db.models import Q
from django.http import Http404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.tenant.models import TenantUser

from .authentications import ESBAuthentication
from .mixins import DefaultTenantMixin
from .permissions import IsAllowedAppCode
from .renderers import BkLegacyApiJSONRenderer
from .serializers import ProfileBatchQueryInputSLZ, ProfileUpdateInputSLZ


class ProfileUpdateApi(DefaultTenantMixin, generics.GenericAPIView):
    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated, IsAllowedAppCode]
    renderer_classes = [BkLegacyApiJSONRenderer]

    def post(self, request, *args, **kwargs):
        """
        更新用户信息
        Note:
          1）在 2.x 中，该接口是 upsert, 而 3.x 中只是 update， 不允许新建用户
          2）在 2.x 中，调用方是 登录 & 桌面，3.x 调整为仅桌面可调用
        """
        slz = ProfileUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        tenant_user = TenantUser.objects.filter(
            Q(id=data["username"]),
            Q(tenant=self.default_tenant),
            Q(data_source__type=DataSourceTypeEnum.REAL)
            | Q(data_source__owner_tenant_id=self.default_tenant.id, data_source__type=DataSourceTypeEnum.VIRTUAL),
        ).first()
        if not tenant_user:
            raise Http404(f"user username:{data['username']} not found")

        # 有传入字段参数则更新
        update_fields = []
        for field in ["language", "time_zone", "wx_userid"]:
            if field in data:
                setattr(tenant_user, field, data[field])
                update_fields.append(field)

        if update_fields:
            update_fields.append("updated_at")
            tenant_user.save(update_fields=update_fields)

        # Note: 由于调用方是判断非 200 即为异常，所以虽然是更新操作，但是兼容接口不可以返回 204，只能是 200
        return Response(status=status.HTTP_200_OK)


class ProfileBatchQueryApi(DefaultTenantMixin, generics.GenericAPIView):
    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated, IsAllowedAppCode]
    renderer_classes = [BkLegacyApiJSONRenderer]

    def post(self, request, *args, **kwargs):
        """
        根据 username 列表, 批量查询用户信息
        """
        slz = ProfileBatchQueryInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        tenant_users = TenantUser.objects.filter(
            Q(id__in=data["username_list"]),
            Q(tenant=self.default_tenant),
            Q(data_source__type=DataSourceTypeEnum.REAL)
            | Q(data_source__owner_tenant_id=self.default_tenant.id, data_source__type=DataSourceTypeEnum.VIRTUAL),
        ).select_related("data_source_user")

        user_infos = []
        for u in tenant_users:
            # 手机号和手机区号
            phone, phone_country_code = u.phone_info
            user_infos.append(
                {
                    # 租户用户 ID 即为对外的 username / bk_username
                    "username": u.id,
                    "chname": u.data_source_user.full_name,
                    "display_name": u.data_source_user.full_name,
                    "email": u.email,
                    "phone": phone,
                    "iso_code": self._phone_country_code_to_iso_code(phone_country_code),
                    "time_zone": u.time_zone,
                    "language": u.language,
                    "wx_userid": u.wx_userid,
                    "qq": "",
                    "role": 0,
                }
            )

        return Response(user_infos)

    @staticmethod
    def _phone_country_code_to_iso_code(phone_country_code: str) -> str:
        """将 86 等手机国际区号 转换 CN 等 ISO 代码"""
        if phone_country_code and phone_country_code.isdigit():
            return phonenumbers.region_code_for_country_code(int(phone_country_code))

        return ""
