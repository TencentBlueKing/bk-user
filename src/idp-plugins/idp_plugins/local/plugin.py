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
from typing import Any, Dict, List

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel

from .db_models import LocalDataSourceIdentityInfo
from ..exceptions import InvalidParamError, UnexpectedDataError
from ..base import BaseCredentialIdpPlugin
from ..models import TestConnectionResult
from ..utils import parse_request_body_json


class LocalIdpPluginConfig(BaseModel):
    """ "本地账密认证源插件配置"""

    # 开启账密登录的数据源
    data_source_ids: List[int] = []


class LocalIdpPlugin(BaseCredentialIdpPlugin):
    """本地账密认证源插件"""

    id = "local"

    config_class = LocalIdpPluginConfig

    def __init__(self, cfg: LocalIdpPluginConfig):
        self.cfg = cfg

    def test_connection(self) -> TestConnectionResult:
        raise NotImplementedError(_("本地认证源不支持连通性测试"))

    def authenticate_credentials(self, request: HttpRequest) -> List[Dict[str, Any]] | Dict[str, Any]:
        """验证账号密码"""
        request_body = parse_request_body_json(request.body)

        username = request_body.get("username")
        if not username:
            raise InvalidParamError(_("用户名不允许为空"))

        password = request_body.get("password")
        if not password:
            raise InvalidParamError(_("密码不允许为空"))

        if not self.cfg.data_source_ids:
            raise UnexpectedDataError(_("当前租户没有数据源允许账密登录"))

        # FIXME (nan): 待用户密码功能改造完成后重新调整校验密码方式
        users = LocalDataSourceIdentityInfo.objects.filter(
            data_source_id__in=self.cfg.data_source_ids, username=username
        )
        matched_users = [i for i in users if i.password == password]

        # TODO：是否需要判断密码过期呢？

        # 判断是否有用户匹配
        if len(matched_users) == 0:
            raise InvalidParamError(_("用户名或密码不正确"))

        return [{"id": i.user.id} for i in matched_users]
