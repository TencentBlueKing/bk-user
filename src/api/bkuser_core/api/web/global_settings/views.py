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

from rest_framework import generics
from rest_framework.response import Response

from bkuser_core.api.web.global_settings.serialziers import GlobalSettingOutputSLZ, GlobalSettingUpdateInputSLZ
from bkuser_core.bkiam.permissions import ManageFieldPermission
from bkuser_core.user_settings.models import GlobalSettings


class GlobalSettingsListUpdateApi(generics.ListAPIView, generics.UpdateAPIView):
    permission_classes = [ManageFieldPermission]  # Note: 以字段管理权限代替全局配置的权限
    serializer_class = GlobalSettingOutputSLZ

    def get_queryset(self):
        namespace = self.kwargs["namespace"]
        return GlobalSettings.objects.filter(namespace=namespace)

    def put(self, request, *args, **kwargs):
        slz = GlobalSettingUpdateInputSLZ(data=request.data, many=True)
        slz.is_valid(raise_exception=True)

        ns_settings = {d["key"]: d["value"] for d in slz.validated_data}
        db_settings = self.get_queryset().filter(key__in=ns_settings.keys())
        for item in db_settings:
            key = item.key
            # 根据当前配置的key， 从ns_settings获取对应key-value
            if key in ns_settings:
                item.value = ns_settings[key]
                item.save()

        return Response()
