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
from dataclasses import dataclass
from typing import Any, List

from django.conf import settings
from iam import IAM, Action, Request, Resource, Subject
from iam.apply.models import (
    ActionWithoutResources,
    ActionWithResources,
    Application,
    BaseAction,
    RelatedResourceType,
    ResourceInstance,
    ResourceNode,
)
from iam.auth.models import ApiBatchAuthRequest, ApiBatchAuthResourceWithPath

from .constants import IAMAction, PrincipalTypeEnum, ResourceType
from .loader import ConfigLoader

iam_logger = logging.getLogger("iam")


@dataclass
class IAMHelper:
    """iam request client"""

    def __post_init__(self):
        self.config_loader = ConfigLoader.from_settings()
        self.app_id_in_iam = self.config_loader.own_app_id or settings.APP_ID
        self.system_id = self.config_loader.system_id
        self.app_token_in_iam = self.config_loader.own_app_token or settings.APP_TOKEN
        self.iam = IAM(self.app_id_in_iam, self.app_token_in_iam, self.config_loader.api_host, settings.BK_PAAS_URL)

    def make_request_without_resources(self, username: str, action_id: IAMAction) -> Request:
        return Request(
            self.system_id,
            Subject(PrincipalTypeEnum.USER.value, username),
            Action(action_id.value),
            None,
            None,
        )

    def make_request_with_resources(self, username: str, action_id: IAMAction, resources: List[Resource]):
        return Request(
            self.system_id,
            Subject(PrincipalTypeEnum.USER.value, username),
            Action(action_id.value),
            resources,
            None,
        )

    def make_resource_attributes(self, obj) -> dict:
        """构造资源属性"""
        return ResourceType.get_attributes_mapping(obj)

    def make_resources_list(self, objs: List[Any]) -> List[List[Resource]]:
        # 探测 obj 类型，包装成 Resource
        # objs 应该都是同一种类型
        resources: list = []
        if not objs:
            return resources

        resource_type = ResourceType.get_by_model(objs[0]).value
        for obj in objs:
            resources.append(
                [
                    Resource(
                        self.system_id,
                        resource_type,
                        str(obj.pk),
                        self.make_resource_attributes(obj),
                    )
                ]
            )
        return resources

    def action_allow(self, username: str, action_id: IAMAction) -> bool:
        """判断用户的某种操作是否有权限"""
        return self.iam.is_allowed(self.make_request_without_resources(username, action_id))

    def objs_action_allow(
        self,
        username: str,
        action_id: IAMAction,
        objs: List[Any],
        any_pass: bool = False,
    ) -> bool:
        """判断用户是否对某些资源的某种操作有权限"""
        if not objs:
            return False

        ret = self.iam.batch_is_allowed(
            resources_list=self.make_resources_list(objs),
            request=self.make_request_without_resources(username=username, action_id=action_id),
        )

        if any_pass:
            return any(ret.values())

        # 当一批操作中存在个别无权限资源，整个操作视为无权限
        return all(ret.values())

    def generate_callback_url(self, username: str, actions: List[IAMAction], obj: Any = None) -> str:
        """生成申请权限回调接口"""

        def get_action(action_id: IAMAction, _obj: Any) -> BaseAction:
            if action_id in IAMAction.get_global_actions():
                return ActionWithoutResources(id=action_id.value)
            else:
                resource_nodes = [ResourceNode(**x) for x in ResourceType.get_instance_resource_nodes(obj)]
                instances = [ResourceInstance(resource_nodes=resource_nodes)] if resource_nodes else []
                related_resource_types = [
                    RelatedResourceType(
                        system_id=self.system_id,
                        type=t.value,
                        instances=instances,
                    )
                    for t in IAMAction.get_related_resource_types(action_id)
                ]

                return ActionWithResources(id=action_id.value, related_resource_types=related_resource_types)

        try:
            actions = [get_action(x, obj) for x in actions]
        except Exception:  # pylint: disable=broad-except
            iam_logger.exception("failed to assemble apply url params")
            return self.config_loader.callback_url

        app = Application(system_id=self.system_id, actions=actions)
        try:
            ok, msg, url = self.iam.get_apply_url(application=app, bk_username=username)
        except Exception:  # pylint: disable=broad-except
            iam_logger.exception("failed to get apply url")
            return self.config_loader.callback_url

        if not ok:
            iam_logger.error("failed to get apply url: %s", msg)
            return self.config_loader.callback_url

        return url

    def create_creator_actions(self, username: str, obj: Any):
        """创建新建关联权限记录"""
        data = {
            "system": self.system_id,
            "type": ResourceType.get_by_model(obj).value,
            "id": ResourceType.get_attr_by_model(obj, index=0),
            "name": ResourceType.get_attr_by_model(obj, index=1),
            "creator": username,
        }
        self.iam.grant_resource_creator_actions(application=data, bk_username=username)

    def create_auth_by_ancestor(
        self,
        username: str,
        ancestor: Any,
        target_type: ResourceType,
        action_ids: List[IAMAction],
    ):
        """通过父对象创建关联权限记录"""
        # 这里是一种特殊的权限关系，只要父对象被授权，所有对应类型的子对象就默认拥有权限
        resources = [
            ApiBatchAuthResourceWithPath(
                system=self.system_id,
                type=target_type,
                paths=[
                    [
                        {
                            "type": ResourceType.get_by_model(ancestor).value,
                            "id": ResourceType.get_attr_by_model(ancestor, index=0),
                            "name": ResourceType.get_attr_by_model(ancestor, index=1),
                        },
                        {"type": target_type, "id": "*", "name": "无限制"},
                    ]
                ],
            )
        ]

        r = ApiBatchAuthRequest(
            system=self.system_id,
            subject=Subject(PrincipalTypeEnum.USER.value, username),
            actions=[Action(x.value) for x in action_ids],
            operate="grant",
            resources=resources,
        )

        self.iam.batch_grant_or_revoke_path_permission(request=r, bk_username=username)

    def get_token(self):
        """获取回调接口所需的 token"""
        return self.iam.get_token(self.system_id)
