# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS
Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class BkUserManager(BaseUserManager):
    """BK user manager"""

    def create_user(self, username, password=None):
        """
        Create and saves a User with the given username and password
        """
        if not username:
            raise ValueError("'The given username must be set")

        now = timezone.now()
        user = self.model(username=username, last_login=now)
        # user.set_password(password)
        # user.save(using=self._db)

        return user
