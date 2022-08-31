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

from .serializers import CategoryMetaSerializer
from bkuser_core.api.web.utils import get_username
from bkuser_core.bkiam.permissions import IAMAction, IAMPermissionExtraInfo, Permission
from bkuser_core.categories.constants import CategoryType


class CategoryMetasListApi(generics.ListAPIView):
    @classmethod
    def make_meta(cls, type_: CategoryType):
        return {
            "type": type_,
            "description": CategoryType.get_description(type_),
            "name": CategoryType.get_choice_label(type_),
        }

    def get(self, request, *args, **kwargs):
        """
        列表展示所有目录类型基本信息
        """
        metas = []
        for type_ in CategoryType.all():
            # 这里目前只返回创建目录类型的权限操作，后期应该可扩展
            try:
                action_id = IAMAction.get_action_by_category_type(type_)
            except KeyError:
                continue

            _meta = self.make_meta(type_)
            # Q：为什么这里需要手动判断权限，而不是通用 permission_classes？
            # A：因为这里的资源（目录类型）是没有对应实体，同时也没有在权限中心注册
            username = get_username(request)
            if not Permission().allow_action_without_resource(username, action_id):
                _meta.update(
                    {
                        "authorized": False,
                        "extra_info": IAMPermissionExtraInfo.from_actions(
                            username=username, action_ids=[action_id]
                        ).to_dict(),
                    }
                )
            metas.append(_meta)

        return Response(CategoryMetaSerializer(metas, many=True).data)
