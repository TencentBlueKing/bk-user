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

from rest_framework import generics
from rest_framework.response import Response

from bkuser.apis.plugin.mixins import PluginApiAccessControlMixin
from bkuser.biz.wecom import WeComAccessTokenManager

from .serializers import WeComAccessTokenInputSLZ, WeComAccessTokenOutputSLZ


class WeComAccessTokenApi(PluginApiAccessControlMixin, generics.RetrieveAPIView):
    """
    获取企业微信 access_token API
    """

    def get(self, request, *args, **kwargs):
        """
        根据 corp_id 和 corp_secret 获取企业微信 access_token
        """
        slz = WeComAccessTokenInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 调用企业微信 access_token 管理器获取 access_token
        token_manager = WeComAccessTokenManager(
            corp_id=data["corp_id"], corp_secret=data["corp_secret"], tenant_id=data["tenant_id"]
        )
        access_token = token_manager.get_access_token()

        return Response(WeComAccessTokenOutputSLZ({"access_token": access_token}).data)
