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
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from bkuser.apps.tenant.models import TenantUser


@receiver(user_logged_in)
def set_timezone(sender, request, user, **kwargs):
    """每次登录读取并添加用户时区信息"""

    # 如果当前会话没有时区信息，则尝试从租户用户模型中获取
    if not request.session[settings.TIME_ZONE_SESSION_KEY]:
        tenant_user = TenantUser.objects.filter(id=user.username).first()
        time_zone = settings.TIME_ZONE

        if tenant_user:
            time_zone = tenant_user.time_zone

        request.session[settings.TIME_ZONE_SESSION_KEY] = time_zone
