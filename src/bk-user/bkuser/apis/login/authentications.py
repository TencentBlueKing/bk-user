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
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed


class BkUserAppAuthentication(BasicAuthentication):
    """
    通过BKUser的AppCode/AppSecret Basic认证
    主要用于项目的login服务调用user服务的服务间接口认证
    """

    def authenticate_credentials(self, userid, password, request=None):
        if userid != settings.BK_APP_CODE or password != settings.BK_APP_SECRET:
            raise AuthenticationFailed("Invalid app_code/app_secret.")

        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(
            username="admin", defaults={"is_active": True, "is_staff": False, "is_superuser": False}
        )
        return user, None
