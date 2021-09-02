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
"""Django project settings
"""


try:
    from django.conf import settings

    APP_ID = settings.APP_ID
    APP_TOKEN = settings.APP_TOKEN
    COMPONENT_SYSTEM_HOST = getattr(settings, "BK_COMPONENT_API_URL", None) or settings.BK_PAAS_URL
    DEFAULT_BK_API_VER = getattr(settings, "DEFAULT_BK_API_VER", "v2")
except Exception:  # pylint: disable=broad-except
    APP_ID = ""
    APP_TOKEN = ""
    COMPONENT_SYSTEM_HOST = ""
    DEFAULT_BK_API_VER = "v2"

CLIENT_ENABLE_SIGNATURE = False
