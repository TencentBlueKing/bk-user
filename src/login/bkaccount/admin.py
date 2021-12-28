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

from __future__ import unicode_literals

from bkaccount.models import Loignlog
from django.contrib import admin


class LoignlogAdmin(admin.ModelAdmin):
    """
    The forms to add and change login log instances.

    The fields to be used in displaying the Loginlog model.
    """

    list_display = ["username", "login_time", "login_browser", "login_ip", "login_host", "app_id"]
    search_fields = ["username"]
    list_filter = ["app_id"]


admin.site.register(Loignlog, LoignlogAdmin)
