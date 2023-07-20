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
from django.conf import settings
from django.utils.translation import ugettext as _

from .utils import is_request_from_esb
from bklogin.bkiam.permissions import Permission


def verify_permission_of_access_app(request, username):
    """
    鉴权：用户是否有访问应用权限
    """
    # 1. 是否开启IAM, 未开启则所有通过
    if not settings.ENABLE_IAM:
        return True, ""

    # 2. 只对ESB来的鉴权，直接调用的不需要鉴权
    if not is_request_from_esb(request):
        return True, ""

    # 3. 获取调用ESB的应用app_code
    verified_app_code = request.META.get("HTTP_X_VERIFIED_BK_APP_CODE")
    if not verified_app_code:
        return True, ""

    # 4. 只对需要访问控制的应用鉴权，其他不需要鉴权
    if verified_app_code not in settings.BK_REQUIRED_ACCESS_CONTROLLED_APPS:
        return True, ""

    is_allowed = Permission().allowed_access_app(username, verified_app_code)
    if is_allowed:
        return True, ""

    return False, _("请联系 {contacts} 开通权限。").format(contacts=", ".join(settings.BK_ACCESS_APP_DENIED_CONTACTS))
