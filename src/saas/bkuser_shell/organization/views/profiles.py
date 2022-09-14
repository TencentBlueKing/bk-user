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

from rest_framework.permissions import IsAuthenticated

import bkuser_sdk
from bkuser_global.drf_crown import inject_serializer
from bkuser_shell.apis.viewset import BkUserApiViewSet
from bkuser_shell.bkiam.constants import IAMAction
from bkuser_shell.common.response import Response
from bkuser_shell.organization.serializers import profiles as serializers
from bkuser_shell.proxy.proxy import BkUserApiProxy

logger = logging.getLogger(__name__)


class ProfilesViewSet(BkUserApiViewSet, BkUserApiProxy):

    permission_classes = [IsAuthenticated]
    ACTION_ID = IAMAction.MANAGE_DEPARTMENT.value

    @inject_serializer(
        body_in=serializers.UpdateProfileSerializer(many=True),
        out=serializers.ProfileSerializer(many=True),
        tags=["profiles"],
    )
    def multiple_update(self, request, validated_data):
        api_instance = bkuser_sdk.BatchApi(self.get_api_client_by_request(request))
        updated_profiles = api_instance.v2_batch_profiles_partial_update(body=validated_data)
        return updated_profiles

    @inject_serializer(body_in=serializers.UpdateProfileSerializer(many=True), tags=["profiles"])
    def multiple_delete(self, request, validated_data):
        api_instance = bkuser_sdk.BatchApi(self.get_api_client_by_request(request))
        api_instance.v2_batch_profiles_delete(body=validated_data)
        return Response()
