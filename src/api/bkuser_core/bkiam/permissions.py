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
from typing import Dict, List, Optional

import regex
from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework.permissions import BasePermission

from .converters import PathIgnoreDjangoQSConverter
from .exceptions import IAMPermissionDenied
from .helper import IAMHelper
from bkuser_core.api.web.utils import get_category, get_department, get_operator, get_profile
from bkuser_core.bkiam.constants import IAMAction, ResourceType
from bkuser_core.departments.models import Department


# FIXME: copy from bkiam/constants.py => 找到单元测试
def _parse_department_path(data):
    """解析 department path"""
    value = data["value"]
    field_map = {"department": "parent_id", "category": "category_id"}
    value_pattern = r"^\/((?P<resource_type>\w+),(?P<resource_id>\d+)\/)+"
    r = regex.match(value_pattern, value).capturesdict()
    r = list(zip(r["resource_type"], r["resource_id"]))

    the_last_of_path = r[-1]
    # 非叶子节点的策略，直接返回路径最后的 id 作为资源 id
    if "node_type" in data and data["node_type"] == "non-leaf":
        field_map["department"] = "id"

    return field_map[the_last_of_path[0]], int(the_last_of_path[1])


CATEGORY_KEY_MAPPING = {"category.id": "id"}

PROFILE_KEY_MAPPING = {"department._bk_iam_path_": _parse_department_path}

DEPARTMENT_KEY_MAPPING = {
    "department.id": "id",
    "department._bk_iam_path_": _parse_department_path,
}


class Permission:
    """
    NOTE: the `operator` should be the username with domain
    - default category: operator = username
    - not default category:  operator = username@domain
    """

    def __init__(self):
        self.iam_enabled = settings.ENABLE_IAM
        # FIXME: 使用新的helper, 隔离老的
        self.helper = IAMHelper()

    # FIXME: 重构, 写注释, 写测试
    def _make_filter(self, operator: str, action_id: IAMAction, key_mapping: Optional[Dict] = None):
        if not self.iam_enabled:
            return None

        iam_request = self.helper.make_request_without_resources(username=operator, action_id=action_id)
        # NOTE: 这里不是给category自己用的, 而是给外检关联表用的, 所以category.id -> category_id
        fs = Permission().helper.iam.make_filter(
            iam_request,
            converter_class=PathIgnoreDjangoQSConverter,
            key_mapping=key_mapping,
        )
        if not fs:
            raise IAMPermissionDenied(
                detail=_("您没有权限进行该操作，请在权限中心申请。"),
                extra_info=IAMPermissionExtraInfo.from_action(operator, action_id.value).to_dict(),
            )
        return fs

    def make_filter_of_category(self, operator: str, action_id: IAMAction, category_id_key: str = "category_id"):
        # NOTE: 这里不是给category自己用的, 而是给外检关联表用的, 所以category.id -> category_id
        return self._make_filter(operator, action_id, {"category.id": category_id_key})

    def make_category_filter(self, operator: str, action_id: IAMAction):
        # NOTE: 这里是给category自己用的, 所以category.id -> id
        return self._make_filter(operator, action_id, CATEGORY_KEY_MAPPING)

    def make_filter_of_department(self, operator: str, action_id: IAMAction):
        # NOTE: 这里给多对多的profile-department用的, 所以解析出来是department.id
        return self._make_filter(operator, action_id, PROFILE_KEY_MAPPING)

    def make_department_filter(self, operator: str, action_id: IAMAction):
        # Note: 过滤Department自身
        return self._make_filter(operator, action_id, DEPARTMENT_KEY_MAPPING)

    def allow_category_action(
        self, operator: str, action_id: IAMAction, category, raise_exception: bool = True
    ) -> bool:
        """如果没有权限并且raise_exception=True, 所有allow_* 必须 raise IAMPermissionDenied"""
        if not self.iam_enabled:
            return True

        objs = [category]
        allowed = self.helper.objs_action_allow(
            action_id=action_id,
            username=operator,
            objs=objs,
        )
        if not allowed and raise_exception:
            raise IAMPermissionDenied(
                detail=_("您没有权限进行该操作，请在权限中心申请。"),
                extra_info=IAMPermissionExtraInfo.from_action(operator, action_id, category).to_dict(),
            )
        return allowed

    def allow_department_action(
        self, operator: str, action_id: IAMAction, department, raise_exception: bool = True
    ) -> bool:
        """如果没有权限并且raise_exception=True, 所有allow_* 必须 raise IAMPermissionDenied"""
        if not self.iam_enabled:
            return True

        objs = [department]
        # FIXME: 去掉对helper的依赖, 直接依赖自己的封装, 便于删除原来的所有代码
        allowed = self.helper.objs_action_allow(
            action_id=action_id,
            username=operator,
            objs=objs,
        )
        if not allowed and raise_exception:
            raise IAMPermissionDenied(
                detail=_("您没有权限进行该操作，请在权限中心申请。"),
                extra_info=IAMPermissionExtraInfo.from_action(operator, action_id, department).to_dict(),
            )
        return allowed

    def allow_tree_departments_action(
        self, operator: str, action_id: IAMAction, departments, raise_exception: bool = True
    ) -> bool:
        """如果没有权限并且raise_exception=True, 所有allow_* 必须 raise IAMPermissionDenied"""
        # 叶节点到根节点的所有部门, 有一个有权限, 则有权限
        if not self.iam_enabled:
            return True

        objs = departments
        allowed = self.helper.objs_action_allow(
            username=operator,
            action_id=action_id,
            objs=objs,
            any_pass=True,
        )
        if not allowed and raise_exception:
            raise IAMPermissionDenied(
                detail=_("您没有权限进行该操作，请在权限中心申请。"),
                extra_info=IAMPermissionExtraInfo.from_action(operator, action_id, departments[0]).to_dict(),
            )
        return allowed

    def allow_action_without_resource(self, operator: str, action_id: IAMAction, raise_exception: bool = True):
        """如果没有权限并且raise_exception=True, 所有allow_* 必须 raise IAMPermissionDenied"""
        if not self.iam_enabled:
            return True
        allowed = self.helper.action_allow(username=operator, action_id=action_id)
        if not allowed and raise_exception:
            raise IAMPermissionDenied(
                detail=_("您没有权限进行该操作，请在权限中心申请。"),
                extra_info=IAMPermissionExtraInfo.from_action(operator, action_id).to_dict(),
            )
        return allowed


# TODO: use with_cache to speed up


# pylint: disable=function-name-too-long
def new_action_without_resource_permission(action_id: IAMAction):
    class ActionWithoutResourcePermission(BasePermission):
        def has_permission(self, request, view):
            operator = get_operator(request)
            return Permission().allow_action_without_resource(operator, action_id)

    return ActionWithoutResourcePermission


def new_category_permission(action_id: IAMAction):
    class CategoryIdInURLPermission(BasePermission):
        def has_permission(self, request, view):
            category_id = view.kwargs["id"]
            category = get_category(category_id)
            operator = get_operator(request)
            return Permission().allow_category_action(operator, action_id, category)

    return CategoryIdInURLPermission


def new_department_permission(action_id: IAMAction):
    class DepartmentIdInURLPermission(BasePermission):
        def has_permission(self, request, view):
            department_id = view.kwargs["id"]
            department = get_department(department_id)
            operator = get_operator(request)
            return Permission().allow_department_action(operator, action_id, department)

    return DepartmentIdInURLPermission


# pylint: disable=function-name-too-long
def new_department_permission_via_profile(action_id: IAMAction):
    class ProfileIdInURLPermission(BasePermission):
        def has_permission(self, request, view):
            # 只要有一级目录有权限, 就是有权限
            operator = get_operator(request)

            profile_id = view.kwargs["id"]
            profile = get_profile(profile_id)
            # BUG: 当用户不属于任何部门时, 这里id__in为空, 会导致部门列表空 => 此时鉴权会返回 False, 导致前端弹无权限报错
            profile_department_ids = profile.departments.values_list("id", flat=True)

            if profile_department_ids:
                departments = Department.tree_objects.get_queryset_ancestors(
                    queryset=Department.objects.filter(id__in=profile_department_ids),
                    include_self=True,
                )
                return Permission().allow_tree_departments_action(operator, action_id, departments)
            else:
                # 此时fallback到检查 用户有没有目录权限
                category = get_category(profile.category_id)
                operator = get_operator(request)
                return Permission().allow_category_action(operator, IAMAction.MANAGE_CATEGORY, category)

    return ProfileIdInURLPermission


# 不关联资源实例的权限控制 Permission Classes
ViewAuditPermission = new_action_without_resource_permission(IAMAction.VIEW_AUDIT)
ManageFieldPermission = new_action_without_resource_permission(IAMAction.MANAGE_FIELD)
# NOT USED YET
# ViewFieldPermission = new_action_without_resource_permission(IAMAction.VIEW_FIELD)
ManageCategoryPermission = new_category_permission(IAMAction.MANAGE_CATEGORY)
ViewCategoryPermission = new_category_permission(IAMAction.VIEW_CATEGORY)
ManageDepartmentPermission = new_department_permission(IAMAction.MANAGE_DEPARTMENT)
ViewDepartmentPermission = new_department_permission(IAMAction.VIEW_DEPARTMENT)

ManageDepartmentProfilePermission = new_department_permission_via_profile(IAMAction.MANAGE_DEPARTMENT)

# FIXME: remove this later
# @dataclass
# class IAMPermission(IAMMiXin, BasePermission):
#     """权限中心权限器，仅控制简单权限操作"""

#     message = _("您没有权限进行该操作，请在权限中心申请。")

#     def __post_init__(self):
#         if settings.ENABLE_IAM:
#             self.helper = IAMHelper()

#     def has_permission(self, request, view) -> bool:
#         """判断某一种操作是否有权限"""
#         if not need_iam(request):
#             return True

#         # no need for auth
#         request.authenticators = ()
#         action_id = self._get_action_id(request)
#         if not IAMAction.is_global_action(action_id):
#             # 只有全局操作项才会直接检视操作，其他而是由 filter or check_obj_permission 控制
#             return True

#         return self.helper.action_allow(action_id=action_id, username=self._get_username(request))

#     def has_object_permission(self, request, view, obj) -> bool:
#         """判断某一种操作在某一个（些）实例上是否有权限"""
#         if not need_iam(request):
#             return True

#         # no need for auth
#         request.authenticators = ()
#         action_id = self._get_action_id(request)
#         if IAMAction.is_global_action(action_id):
#             # 由 has_permission 控制
#             return True

#         # TODO: 针对 department 做了特殊处理，更通用的做法？
#         any_pass = False
#         objs = [obj]
#         if isinstance(obj, Department):
#             any_pass = True
#             objs = obj.get_ancestors(include_self=True)

#         if isinstance(obj, Profile):
#             any_pass = True
#             objs = Department.tree_objects.get_queryset_ancestors(
#                 queryset=Department.objects.filter(id__in=obj.departments.values_list("id", flat=True)),
#                 include_self=True,
#             )

#         return self.helper.objs_action_allow(
#             action_id=action_id,
#             username=self._get_username(request),
#             objs=objs,
#             any_pass=any_pass,
#         )


@dataclass
class RelatedResource:
    id: str
    name: str
    type: str
    type_name: str

    @classmethod
    def from_obj(cls, obj) -> Optional["RelatedResource"]:
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


@dataclass
class AuthInfo:

    id: IAMAction
    display_name: str
    related_resources: List[RelatedResource]

    @classmethod
    def from_action(cls, action: IAMAction, obj=None) -> "AuthInfo":
        related_resource = RelatedResource.from_obj(obj)
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


@dataclass
class IAMPermissionExtraInfo:

    auth_infos: List[AuthInfo]
    callback_url: str

    @classmethod
    def from_action(cls, username: str, action_id: str, obj=None) -> "IAMPermissionExtraInfo":
        helper = IAMHelper()
        action = IAMAction(action_id)

        return cls(
            auth_infos=[AuthInfo.from_action(action, obj)],
            callback_url=helper.generate_callback_url(username=username, actions=[action], obj=obj),
        )

    @classmethod
    def from_actions(cls, username: str, action_ids: List[IAMAction]) -> "IAMPermissionExtraInfo":
        helper = IAMHelper()

        return cls(
            auth_infos=[AuthInfo.from_action(x) for x in action_ids],
            callback_url=helper.generate_callback_url(username=username, actions=action_ids),
        )

    def to_dict(self):
        return {
            "auth_infos": [x.to_dict() for x in self.auth_infos],
            "callback_url": self.callback_url,
        }
