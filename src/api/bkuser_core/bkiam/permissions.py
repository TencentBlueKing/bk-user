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
from dataclasses import dataclass
from typing import List

from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework.permissions import BasePermission

from .base import IAMMiXin
from .helper import IAMHelper
from .utils import need_iam
from bkuser_core.bkiam.constants import IAMAction, ResourceType
from bkuser_core.departments.models import Department
from bkuser_core.profiles.models import Profile


@dataclass
class IAMPermission(IAMMiXin, BasePermission):
    """权限中心权限器，仅控制简单权限操作"""

    message = _("您没有权限进行该操作，请在权限中心申请。")

    def __post_init__(self):
        if settings.ENABLE_IAM:
            self.helper = IAMHelper()

    def has_permission(self, request, view) -> bool:
        """判断某一种操作是否有权限"""
        if not need_iam(request):
            return True

        # no need for auth
        request.authenticators = ()
        action_id = self._get_action_id(request)
        if not IAMAction.is_global_action(action_id):
            # 只有全局操作项才会直接检视操作，其他而是由 filter or check_obj_permission 控制
            return True

        return self.helper.action_allow(action_id=action_id, username=self._get_username(request))

    def has_object_permission(self, request, view, obj) -> bool:
        """判断某一种操作在某一个（些）实例上是否有权限"""
        if not need_iam(request):
            return True

        # no need for auth
        request.authenticators = ()
        action_id = self._get_action_id(request)
        if IAMAction.is_global_action(action_id):
            # 由 has_permission 控制
            return True

        # TODO: 针对 department 做了特殊处理，更通用的做法？
        any_pass = False
        objs = [obj]
        if isinstance(obj, Department):
            any_pass = True
            objs = obj.get_ancestors(include_self=True)

        if isinstance(obj, Profile):
            any_pass = True
            objs = Department.tree_objects.get_queryset_ancestors(
                queryset=Department.objects.filter(id__in=obj.departments.values_list("id", flat=True)),
                include_self=True,
            )

        return self.helper.objs_action_allow(
            action_id=action_id,
            username=self._get_username(request),
            objs=objs,
            any_pass=any_pass,
        )


@dataclass
class IAMPermissionExtraInfo(IAMMiXin):
    @dataclass
    class AuthInfo:
        @dataclass
        class RelatedResource:
            id: str
            name: str
            type: str
            type_name: str

            @classmethod
            def from_obj(cls, obj):
                if not obj:
                    return None

                name_field_name = ResourceType.get_constants_by_model(obj, "get_id_name_pair")[1]
                return cls(
                    id=str(obj.pk),
                    name=getattr(obj, name_field_name, "-"),
                    type=ResourceType.get_by_model(obj).value,
                    type_name=ResourceType.get_type_name(ResourceType.get_by_model(obj)),
                )

            def to_dict(self):
                return {
                    "id": self.id,
                    "name": self.name,
                    "type": self.type,
                    "type_name": self.type_name,
                }

        id: IAMAction
        display_name: str
        related_resources: List[RelatedResource]

        @classmethod
        def from_action(cls, action: IAMAction, obj=None):
            related_resource = cls.RelatedResource.from_obj(obj)
            return cls(
                id=action.value,
                display_name=IAMAction.get_choice_label(action),
                related_resources=[related_resource] if related_resource else [],
            )

        def to_dict(self):
            return {
                "id": self.id,
                "display_name": self.display_name,
                "related_resources": [x.to_dict() for x in self.related_resources],
            }

    auth_infos: List[AuthInfo]
    callback_url: str

    @classmethod
    def from_request(cls, request, obj=None) -> "IAMPermissionExtraInfo":
        helper = IAMHelper()
        action = cls._get_action_id(request)

        return cls(
            auth_infos=[cls.AuthInfo.from_action(action, obj)],
            callback_url=helper.generate_callback_url(username=request.operator, actions=[IAMAction(action)], obj=obj),
        )

    @classmethod
    def from_actions(cls, username: str, action_ids: List[IAMAction]) -> "IAMPermissionExtraInfo":
        helper = IAMHelper()

        return cls(
            auth_infos=[cls.AuthInfo.from_action(x) for x in action_ids],
            callback_url=helper.generate_callback_url(username=username, actions=action_ids),
        )

    def to_dict(self):
        return {
            "auth_infos": [x.to_dict() for x in self.auth_infos],
            "callback_url": self.callback_url,
        }
