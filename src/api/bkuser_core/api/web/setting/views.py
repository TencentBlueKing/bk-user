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

from .serializers import SettingMetaOutputSLZ, SettingMetasListInputSLZ
from bkuser_core.api.web.constants import EXCLUDE_SETTINGS_META_IN_META_LISTVIEW
from bkuser_core.user_settings.models import SettingMeta

# from bkuser_core.bkiam.permissions import ManageFieldPermission


class SettingMetasListApi(generics.ListAPIView):
    # NOTE: 后台没有任何权限管控(这个是全局的, 不关联任何目录/资源), 这里暂时使用 MANAGE_FIELD 权限替代, FIXME: 切分独立权限, 替换这里
    # FIXME: 目前无法加权限, 加上会导致前端先弹窗这个, 在弹窗真正需要申请的权限(因为页面同时加载了多个api), 非敏感信息
    # permission_classes = [ManageFieldPermission]
    serializer_class = SettingMetaOutputSLZ

    def get_queryset(self):
        slz = SettingMetasListInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        category_type = data["category_type"]
        namespace = data["namespace"]

        queryset = SettingMeta.objects.filter(category_type=category_type).exclude(
            key__in=EXCLUDE_SETTINGS_META_IN_META_LISTVIEW
        )
        if namespace:
            queryset = queryset.filter(namespace=namespace)
        return queryset
