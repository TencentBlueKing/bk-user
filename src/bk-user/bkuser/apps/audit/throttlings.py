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

from django.conf import settings
from django.core.cache import caches
from rest_framework.throttling import SimpleRateThrottle


class OpenWebApiThrottling(SimpleRateThrottle):
    cache = caches["redis"]

    def get_cache_key(self, request, view):
        # 缓存 key 为 scope（调用接口类型） + 调用者 bk_username
        scope = getattr(view, "throttle_scope", self.scope)
        return self.cache_format % {"scope": scope, "ident": request.user.username}

    def get_rate(self):
        # 直接从环境变量中读取 rate
        return settings.OPENWEB_API_THROTTLE_RATES
