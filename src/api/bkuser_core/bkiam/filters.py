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
# FIXME: remove this file after all filter logical in new codes are ok

# from dataclasses import dataclass

# from django.utils.translation import ugettext_lazy as _
# from rest_framework import filters

# from .base import IAMMiXin
# from .constants import ResourceType
# from .converters import PathIgnoreDjangoQSConverter
# from .exceptions import IAMPermissionDenied
# from .helper import IAMHelper
# from .permissions import IAMPermissionExtraInfo
# from .utils import need_iam

# @dataclass
# class IAMFilter(filters.BaseFilterBackend):
#     """权限中心过滤器"""

#     def __post_init__(self):
#         self.helper = IAMHelper()

#     def filter_queryset(self, request, queryset, view):
#         """根据权限项筛选有权限的内容"""
#         if not need_iam(request):
#             return queryset

#         if not queryset:
#             return queryset

#         iam_request = self.helper.make_request_without_resources(
#             username=self._get_username(request), action_id=self._get_action_id(request)
#         )
#         fs = self.helper.iam.make_filter(
#             iam_request,
#             converter_class=PathIgnoreDjangoQSConverter,
#             key_mapping=ResourceType.get_constants_by_model(queryset[0], "get_key_mapping"),
#         )
#         if not fs:
#             raise IAMPermissionDenied(
#                 detail=_("您没有权限进行该操作，请在权限中心申请。"),
#                 extra_info=IAMPermissionExtraInfo.from_request(request).to_dict(),
#             )

#         return queryset.filter(fs)
