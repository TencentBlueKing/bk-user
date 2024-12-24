# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
from collections import namedtuple

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

InnerBearerToken = namedtuple("InnerBearerToken", ["verified"])


class InnerBearerTokenAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def __init__(self):
        self.allowed_tokens = [settings.BK_APIGW_TO_BK_USER_INNER_BEARER_TOKEN]

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed("Invalid token header. No credentials provided.")
        if len(auth) > 2:  # noqa: PLR2004
            raise exceptions.AuthenticationFailed("Invalid token header. Token string should not contain spaces.")

        try:
            token = auth[1].decode()
        except UnicodeError:
            raise exceptions.AuthenticationFailed(
                "Invalid token header. Token string should not contain invalid characters."
            )

        # Verify Bearer Token
        if token not in self.allowed_tokens:
            raise exceptions.AuthenticationFailed("Invalid token.")

        # Mark Verified Bearer Token
        request.inner_bearer_token = InnerBearerToken(verified=True)

        return AnonymousUser(), None
