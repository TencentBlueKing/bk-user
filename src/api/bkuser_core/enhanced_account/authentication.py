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
import base64
import logging
import re

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import caches
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from bkuser_core.esb_sdk.shortcuts import get_client_by_raw_username

logger = logging.getLogger(__name__)


HEADER_JWT_KEY_NAME = "HTTP_X_BKAPI_JWT"
HEADER_APP_CODE_KEY_NAME = "HTTP_X_BK_APP_CODE"
HEADER_APP_SECRET_KEY_NAME = "HTTP_X_BK_APP_SECRET"

ESB_PUBLIC_KEY_CACHE_KEY = "bk_user:esb_public_key"

TOKEN_KEY_NAME = "token"


def create_user(username="admin"):
    return get_user_model()(username=username, is_staff=True, is_superuser=True)


class InternalTokenAuthentication(BaseAuthentication):

    keyword = "iBearer"
    model = None

    query_params_keyword = TOKEN_KEY_NAME

    def get_token_from_query_params(self, request):
        try:
            return request.query_params[self.query_params_keyword]
        except KeyError:
            msg = f"Invalid token header. No credentials provided. {self.query_params_keyword} is not in query params"
            raise exceptions.AuthenticationFailed(msg)

    def get_token_from_header(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            msg = "Invalid token header. No credentials provided. The format should be `iBearer THE_TOKEN`"
            raise exceptions.AuthenticationFailed(msg)

        if len(auth) == 1:
            msg = "Invalid token header. No credentials provided. The size of auth array credentials is 0"
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = (
                "Invalid token header. Token string should not contain spaces. "
                + "The size of auth array credentials is more than 2"
            )
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = "Invalid token header. Token string should not contain invalid characters."
            raise exceptions.AuthenticationFailed(msg)

        return token

    def authenticate(self, request):
        try:
            token = self.get_token_from_query_params(request)
        except exceptions.AuthenticationFailed:
            logger.debug("no token from query params, trying to get from header instead")
            token = self.get_token_from_header(request)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        """Use access token to identify user"""
        if key in settings.INTERNAL_AUTH_TOKENS:
            user_info = settings.INTERNAL_AUTH_TOKENS[key]
            return create_user(user_info["username"]), None
        raise exceptions.AuthenticationFailed(
            "request failed: Invalid token header. No credentials provided or Wrong credentials."
        )


class ESBOrAPIGatewayAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # get jwt from header
        jwt_content = request.META.get(HEADER_JWT_KEY_NAME, "")
        if not jwt_content:
            return None, None

        # get the public key
        jwt_header = jwt.get_unverified_header(jwt_content)
        api_name = jwt_header.get("kid") or ""
        public_key = self._get_public_key(api_name)
        algorithm = jwt_header.get("alg") or "RS512"

        # do decode, without verify issuer
        try:
            jwt_playload = jwt.decode(jwt_content, public_key, algorithm)
        except Exception:  # pylint: disable=broad-except
            logger.exception("JWT decode failed! jwt_payload: %s, public_key: %s", jwt_content, public_key)
            raise exceptions.AuthenticationFailed("decode jwt token fail")

        # username = self._get_username_from_jwt_payload(payload)
        app_code = self._get_app_code_from_jwt_payload(jwt_playload)
        request.bk_app_code = app_code

        username = "APIGW" if api_name == settings.BK_APIGW_NAME else "ESB"
        return create_user(username), None

    def _get_public_key(self, api_name):
        # it's from apigateway
        if api_name == settings.BK_APIGW_NAME:
            return self._get_apigw_public_key()
        # it's from esb
        else:
            return self._get_esb_public_key()

    def _get_apigw_public_key(self):
        """
        获取APIGW的PUBLIC KEY
        由于配置文件里的public key 是来着环境变量，且使用了base64编码的，所以需要获取后解码
        """
        # 如果BK_APIGW_PUBLIC_KEY为空，则直接报错
        if not settings.BK_APIGW_PUBLIC_KEY:
            raise exceptions.AuthenticationFailed("BK_APIGW_PUBLIC_KEY can not be empty")

        # base64解码
        try:
            public_key = base64.b64decode(settings.BK_APIGW_PUBLIC_KEY).decode("utf-8")
        except Exception:  # pylint: disable=broad-except
            logger.exception(
                "BK_APIGW_PUBLIC_KEY is not valid base64 string! public_key=%s", settings.BK_APIGW_PUBLIC_KEY
            )
            raise exceptions.AuthenticationFailed("BK_APIGW_PUBLIC_KEY is not valid base64 string!")

        return public_key

    def _get_esb_public_key(self):
        cache = caches["locmem"]
        public_key = cache.get(ESB_PUBLIC_KEY_CACHE_KEY)
        if public_key is not None:
            return public_key

        # get from esb
        client = get_client_by_raw_username("admin")
        try:
            ret = client.esb.get_public_key()
        except Exception:  # pylint: disable=broad-except
            logger.exception("Get ESB Public Key failed!")
            raise exceptions.AuthenticationFailed("Get ESB Public Key failed!")

        if not ret.get("result", False):
            msg = ret.get("message", "unknown error")
            logger.error("Get ESB Public Key failed! %s", msg)
            raise exceptions.AuthenticationFailed(f"Get ESB Public Key failed! {msg}")

        public_key = ret.get("data", {}).get("public_key", "")
        if public_key is None:
            logger.error("Get ESB Public Key failed! public_key is empty, ret=%s", ret)
            raise exceptions.AuthenticationFailed("Get ESB Public Key failed! the public key is empty")

        cache.set(ESB_PUBLIC_KEY_CACHE_KEY, public_key, 60 * 60)
        return public_key

    def _get_app_code_from_jwt_payload(self, jwt_payload):
        """从jwt里获取app_code"""
        app = jwt_payload.get("app", {})

        verified = app.get("verified", False)
        if not verified:
            raise exceptions.AuthenticationFailed("app is not verified")

        app_code = app.get("bk_app_code", "") or app.get("app_code", "")
        # 虽然app_code为空对于后续的鉴权一定是不通过的，但鉴权不通过有很多原因，这里提前log便于问题排查
        if not app_code:
            raise exceptions.AuthenticationFailed("could not get app_code from esb/apigateway jwt payload! it's empty")

        return app_code


class AppCodeAppSecretAuthentication(BaseAuthentication):
    """
    通过app_code和app_secret进行鉴权
    """

    def authenticate(self, request):
        # get app_code and app_secret from header
        app_code = request.META.get(HEADER_APP_CODE_KEY_NAME, "")
        app_secret = request.META.get(HEADER_APP_SECRET_KEY_NAME, "")

        if app_code == settings.APP_ID and app_secret == settings.APP_TOKEN:
            return create_user("SAAS"), None

        return None, None


class MultipleAuthentication(BaseAuthentication):
    """it's a dispatcher"""

    def authenticate(self, request):
        # FIXME: 最终, 下掉token, 只保留 jwt + app_code/app_secret
        # withe list
        for white_url in settings.AUTH_EXEMPT_PATHS:
            if re.search(white_url, request.path):
                logger.debug("%s path in white_url<%s>, exempting auth", request.path, white_url)
                return None, None

        # app_code and app_secret
        if HEADER_APP_CODE_KEY_NAME in request.META and HEADER_APP_SECRET_KEY_NAME in request.META:
            return AppCodeAppSecretAuthentication().authenticate(request)

        # FIXME: should remove this totally
        # NOTE: some case we want to use token as credentials, call through APIGateway(set default headers)
        # so we should verify others first, not jwt
        if get_authorization_header(request) or request.query_params.get(TOKEN_KEY_NAME):
            # token
            return InternalTokenAuthentication().authenticate(request)

        # jwt
        if HEADER_JWT_KEY_NAME in request.META:
            return ESBOrAPIGatewayAuthentication().authenticate(request)

        raise exceptions.AuthenticationFailed(
            "no valid authentication credentials provided! should call through APIGateway/ESB"
        )
