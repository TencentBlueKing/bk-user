# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import base64
import logging
from typing import Any, Dict

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request

from bkuser.common.cache import cachedmethod
from bkuser.common.constants import BKNonEntityUser
from bkuser.component import esb

logger = logging.getLogger(__name__)


class ESBAuthentication(BaseAuthentication):
    def authenticate(self, request):
        """
        认证凭证信息，返回认证后的 Django User，同时设置 request.bk_app_code 便于后续鉴权判断请求来源
        """
        credentials = self.get_credentials(request)

        if not credentials:
            return None

        payload = self.verify_credentials(credentials=credentials)
        if payload is None:
            return None

        username = self._get_username_from_jwt_payload(payload)
        app_code = self._get_app_code_from_jwt_payload(payload)

        # 获取到调用 app_code
        request.bk_app_code = app_code

        return self._get_or_create_user(username), None

    def get_credentials(self, request: Request) -> Dict[str, str] | None:
        """从 Header 头获取接口认证的凭证信息"""
        credentials = {
            "jwt": request.META.get("HTTP_X_BKAPI_JWT"),
            "from": request.META.get("HTTP_X_BKAPI_FROM", "esb"),
        }
        # Return None if some are empty
        if all(credentials.values()):
            return credentials

        return None

    def verify_credentials(self, credentials: Dict[str, str]) -> Dict[str, Any] | None:
        """JWT 校验并解析出调用方信息"""
        public_key = self._get_jwt_public_key(credentials["from"])
        # Note: 不从 jwt header 里取 kid 判断是网关还是 ESB 签发的，在不同环境可能不准确
        jwt_payload = self._decode_jwt(credentials["jwt"], public_key)
        if not jwt_payload:
            return None

        return jwt_payload

    def _decode_jwt(self, content: str, public_key: str) -> Dict[str, Any] | None:
        """解析 JWT"""
        try:
            jwt_header = jwt.get_unverified_header(content)
            algorithm = jwt_header.get("alg") or "RS512"
            return jwt.decode(content, public_key, algorithms=[algorithm], options={"verify_iss": False})
        except Exception:  # pylint: disable=broad-except
            logger.exception("decode jwt fail, jwt: %s", content)
            return None

    def _get_username_from_jwt_payload(self, jwt_payload: Dict[str, Any]) -> str:
        """从 jwt payload 里获取 username"""
        user = jwt_payload.get("user", {})
        verified = user.get("verified", False)
        username = user.get("bk_username", "") or user.get("username", "")
        # 如果 user 通过认证，则为实体用户，直接返回
        if verified:
            return username

        # 未通过认证有两种可能，（1）username 不可信任（2）username 为空
        # 非空则说明是未认证，不可信任的用户，则统一用不可信任的用户名代替，不使用传递过来的 username
        if username:
            return BKNonEntityUser.BK__UNVERIFIED_USER.value

        # 匿名用户
        return BKNonEntityUser.BK__ANONYMOUS_USER.value

    def _get_app_code_from_jwt_payload(self, jwt_payload: Dict[str, Any]) -> str:
        """从 jwt payload 里获取 app_code"""
        app = jwt_payload.get("app", {})

        if not app.get("verified", False):
            raise exceptions.AuthenticationFailed("app is not verified")

        # 兼容多版本(企业版/TE版/社区版) 以及兼容 APIGW / ESB
        app_code = app.get("bk_app_code", "") or app.get("app_code", "")

        # 虽然 app_code 为空对于后续的鉴权一定是不通过的，但鉴权不通过有很多原因，这里提前log便于问题排查
        if not app_code:
            raise exceptions.AuthenticationFailed("could not get app_code from esb/apigateway jwt payload! it's empty")

        return app_code

    def _get_or_create_user(self, username):
        """获取或创建标准  Django User，用于通过认证"""
        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(
            username=username, defaults={"is_active": True, "is_staff": False, "is_superuser": False}
        )
        return user

    def _get_apigw_public_key(self) -> str:
        """
        获取 APIGW 的 Public Key
        由于配置文件里的 public key 是来自环境变量，且使用 base64 编码，因此需要解码
        """
        # 如果 BK_APIGW_PUBLIC_KEY 为空，则直接报错
        if not settings.BK_APIGW_PUBLIC_KEY:
            logger.error("BK_APIGW_PUBLIC_KEY can not be empty")
            return ""

        try:
            public_key = base64.b64decode(settings.BK_APIGW_PUBLIC_KEY).decode("utf-8")
        except Exception:  # pylint: disable=broad-except
            logger.exception("BK_APIGW_PUBLIC_KEY is not the base64 string, base64.b64decode fail")
            return ""

        return public_key

    @cachedmethod(timeout=None)  # 缓存不过期，除非重新部署服务
    def _get_jwt_public_key(self, request_from: str) -> str:
        """根据来源，获取 Jwt Public Key"""
        # TODO 理论上 open_v2 只接 ESB，open_v3 只接 APIGW，后续新增 open_v3 后可以分离该 Auth 类逻辑
        if request_from == "apigw":
            return self._get_apigw_public_key()

        return esb.get_api_public_key()["public_key"]
