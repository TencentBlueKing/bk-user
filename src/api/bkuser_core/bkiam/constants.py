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
from enum import auto
from typing import Any, Callable, Dict, List

from django.utils.translation import ugettext_lazy as _

from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.models import ProfileCategory, SyncTask
from bkuser_core.common.enum import AutoLowerEnum
from bkuser_core.departments.models import Department
from bkuser_core.profiles.models import DynamicFieldInfo, Profile


class IAMCallbackMethods(AutoLowerEnum):
    LIST_ATTR = auto()
    LIST_ATTR_VALUE = auto()
    LIST_INSTANCE = auto()
    FETCH_INSTANCE_INFO = auto()
    LIST_INSTANCE_BY_POLICY = auto()
    SEARCH_INSTANCE = auto()

    _choices_labels = (
        (LIST_ATTR, _("查询某个资源类型可用于配置权限的属性列表")),
        (LIST_ATTR_VALUE, _("获取一个资源类型某个属性的值列表")),
        (LIST_INSTANCE, _("根据过滤条件查询实例")),
        (FETCH_INSTANCE_INFO, _("批量获取资源实例详情")),
        (LIST_INSTANCE_BY_POLICY, _("根据策略表达式查询资源实例")),
        (SEARCH_INSTANCE, _("搜索资源实例")),
    )


class PrincipalTypeEnum(AutoLowerEnum):
    USER = auto()


class IAMAction(AutoLowerEnum):

    # 用户字段
    MANAGE_FIELD = auto()
    VIEW_FIELD = auto()

    # 审计
    VIEW_AUDIT = auto()

    # 目录相关
    CREATE_LOCAL_CATEGORY = auto()
    CREATE_LDAP_CATEGORY = auto()
    CREATE_MAD_CATEGORY = auto()
    CREATE_CUSTOM_CATEGORY = auto()
    MANAGE_CATEGORY = auto()
    VIEW_CATEGORY = auto()

    # 部门
    CREATE_ROOT_DEPARTMENT = auto()
    MANAGE_DEPARTMENT = auto()
    VIEW_DEPARTMENT = auto()

    @classmethod
    def get_choice_label(cls, action_id: "IAMAction") -> str:
        return {
            cls.MANAGE_FIELD: _("用户字段管理"),
            cls.VIEW_FIELD: _("查看字段"),
            cls.VIEW_AUDIT: _("审计信息查看"),
            cls.CREATE_LOCAL_CATEGORY: _("本地用户目录新建"),
            cls.CREATE_LDAP_CATEGORY: _("LDAP目录新建"),
            cls.CREATE_MAD_CATEGORY: _("MAD目录新建"),
            cls.CREATE_CUSTOM_CATEGORY: _("自定义目录新建"),
            cls.MANAGE_CATEGORY: _("目录管理"),
            cls.VIEW_CATEGORY: _("查看目录"),
            cls.CREATE_ROOT_DEPARTMENT: _("根组织新建"),
            cls.MANAGE_DEPARTMENT: _("组织和成员管理"),
            cls.VIEW_DEPARTMENT: _("组织和成员查看"),
        }[action_id]

    @classmethod
    def get_global_actions(cls) -> tuple:
        """不需要和任何资源绑定，只需要判断某人是否有某个操作的权限"""
        return (
            cls.VIEW_AUDIT,
            cls.VIEW_FIELD,
            cls.MANAGE_FIELD,
            cls.CREATE_MAD_CATEGORY,
            cls.CREATE_LDAP_CATEGORY,
            cls.CREATE_LOCAL_CATEGORY,
            cls.CREATE_CUSTOM_CATEGORY,
        )

    @classmethod
    def get_action_by_category_type(cls, category_type: str) -> "IAMAction":
        # FIXME: move to other place?
        return {  # type: ignore
            CategoryType.LOCAL.value: cls.CREATE_LOCAL_CATEGORY,
            CategoryType.LDAP.value: cls.CREATE_LDAP_CATEGORY,
            CategoryType.MAD.value: cls.CREATE_MAD_CATEGORY,
        }[category_type]

    # @classmethod
    # def is_global_action(cls, action_id: "IAMAction") -> bool:
    #     for i in cls.get_global_actions():
    #         if action_id == i:
    #             return True
    #     return False

    @classmethod
    def get_related_resource_types(cls, action_id: "IAMAction") -> list:
        return {
            cls.MANAGE_CATEGORY: [ResourceType.CATEGORY],
            cls.VIEW_CATEGORY: [ResourceType.CATEGORY],
            cls.VIEW_DEPARTMENT: [ResourceType.DEPARTMENT],
            cls.MANAGE_DEPARTMENT: [ResourceType.DEPARTMENT],
            cls.CREATE_ROOT_DEPARTMENT: [ResourceType.CATEGORY],
        }[action_id]


class ResourceType(AutoLowerEnum):
    FIELD = auto()
    CATEGORY = auto()
    DEPARTMENT = auto()
    PROFILE = auto()
    SYNCTASK = auto()

    @classmethod
    def get_type_name(cls, resource_type: "ResourceType") -> str:
        return {
            cls.FIELD: _("用户字段"),
            cls.CATEGORY: _("用户目录"),
            cls.DEPARTMENT: _("组织"),
            cls.PROFILE: _("用户"),
        }[resource_type]

    @classmethod
    def get_by_model(cls, instance) -> "ResourceType":
        return {  # type: ignore
            Department: cls.DEPARTMENT,
            ProfileCategory: cls.CATEGORY,
            DynamicFieldInfo: cls.FIELD,
            Profile: cls.PROFILE,
            SyncTask: cls.SYNCTASK,
        }[type(instance)]

    @classmethod
    def get_attr_by_model(cls, instance, index: int) -> str:
        """通过 model instance 获取"""
        type_ = cls.get_by_model(instance)
        id_name_pair = cls.get_id_name_pair(type_)
        return getattr(instance, id_name_pair[index])

    @classmethod
    def get_attributes_mapping(cls, instance) -> dict:
        """获取模型和权限中心属性对应"""

        def get_department_path_attribute(obj):
            start = f"/category,{obj.category_id}/"
            ancestor_ids = obj.get_ancestors(include_self=True).values_list("id", flat=True)
            for ancestor_id in ancestor_ids:
                start += f"department,{ancestor_id}/"

            return {"_bk_iam_path_": start}

        _map: Dict[Any, Callable] = {
            cls.DEPARTMENT: get_department_path_attribute,
        }
        try:
            return _map[cls.get_by_model(instance)](instance)
        except KeyError:
            return {}

    # @classmethod
    # def get_key_mapping(cls, resource_type: "ResourceType") -> dict:
    #     def parse_department_path(data):
    #         """解析 department path"""
    #         value = data["value"]
    #         field_map = {"department": "parent_id", "category": "category_id"}
    #         value_pattern = r"^\/((?P<resource_type>\w+),(?P<resource_id>\d+)\/)+"
    #         r = regex.match(value_pattern, value).capturesdict()
    #         r = list(zip(r["resource_type"], r["resource_id"]))

    #         the_last_of_path = r[-1]
    #         # 非叶子节点的策略，直接返回路径最后的 id 作为资源 id
    #         if "node_type" in data and data["node_type"] == "non-leaf":
    #             field_map["department"] = "id"

    #         return field_map[the_last_of_path[0]], int(the_last_of_path[1])

    #     _map: Dict[Any, dict] = {
    #         cls.DEPARTMENT: {
    #             "department.id": "id",
    #             "department._bk_iam_path_": parse_department_path,
    #         },
    #         cls.CATEGORY: {"category.id": "id"},
    #         cls.FIELD: {"field.id": "name"},
    #         cls.PROFILE: {
    #             "department._bk_iam_path_": parse_department_path,
    #         },
    #         cls.SYNCTASK: {"category.id": "category_id"},
    #     }
    #     return _map[resource_type]

    @classmethod
    def get_id_name_pair(cls, resource_type: "ResourceType") -> tuple:
        """获取 id name 对"""
        _map: Dict[Any, tuple] = {
            cls.DEPARTMENT: ("id", "name"),
            cls.CATEGORY: ("id", "display_name"),
            cls.FIELD: ("id", "display_name"),
            cls.PROFILE: ("id", "username"),
            # FIXME: not sure
            cls.SYNCTASK: ("id", "id"),
        }
        return _map[resource_type]

    @classmethod
    def get_instance_resource_nodes(cls, instance: Any) -> list:
        """通过数据库实例获取依赖授权路径"""
        if not instance:
            return []

        def get_parent_nodes(i: Department) -> List[dict]:
            """获取父路径的 resource nodes"""
            # 请求 callback 需要完整的资源路径
            parents = i.get_ancestors(include_self=True)
            d_nodes = [{"type": cls.get_by_model(d).value, "id": d.pk, "name": d.name} for d in parents]

            category = ProfileCategory.objects.get(id=i.category_id)
            return [
                {"type": cls.CATEGORY.value, "id": category.id, "name": category.display_name},
                *d_nodes,
            ]

        special_map: Dict[Any, Callable] = {
            cls.DEPARTMENT: get_parent_nodes,
        }

        try:
            return special_map[cls.get_by_model(instance)](instance)
        except KeyError:
            return [
                {
                    "type": cls.get_by_model(instance).value,
                    "id": instance.pk,
                    "name": getattr(
                        instance,
                        cls.get_constants_by_model(instance, "get_id_name_pair")[1],
                    ),
                }
            ]

    @classmethod
    def get_constants_by_model(cls, instance, target: str) -> Any:
        """通过数据模型实例来获取配置常量
        :param instance: 数据模型实例
        :param target: 目标方法
        """
        return getattr(cls, target)(cls.get_by_model(instance))
