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
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

logger = logging.getLogger(__name__)


def create_user(username="admin"):
    return get_user_model()(username=username, is_staff=True, is_superuser=True)


class InternalTokenAuthentication(BaseAuthentication):

    keyword = "iBearer"
    model = None

    query_params_keyword = "token"

    def get_token_from_query_params(self, request):
        try:
            return request.query_params[self.query_params_keyword]
        except KeyError:
            msg = "Invalid token header. No credentials provided."
            raise exceptions.AuthenticationFailed(msg)

    def get_token_from_header(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            msg = "Invalid token header. No credentials provided."
            raise exceptions.AuthenticationFailed(msg)

        if len(auth) == 1:
            msg = "Invalid token header. No credentials provided."
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = "Invalid token header. Token string should not contain spaces."
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = "Invalid token header. Token string should not contain invalid characters."
            raise exceptions.AuthenticationFailed(msg)

        return token

    def authenticate(self, request):
        for white_url in settings.AUTH_EXEMPT_PATHS:
            if re.search(white_url, request.path):
                logger.info("%s path in white_url<%s>, exempting auth", request.path, white_url)
                return None, None

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
        raise exceptions.AuthenticationFailed("request failed: Invalid token header. No credentials provided.")
