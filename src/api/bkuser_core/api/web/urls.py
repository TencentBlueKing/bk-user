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
from django.conf.urls import include, url

# prefix: /api/v1/web
urlpatterns = [
    url(r"^categories/", include("bkuser_core.api.web.category.urls")),
    url(r"^settings/", include("bkuser_core.api.web.setting.urls")),
    url(r"^sync_tasks/", include("bkuser_core.api.web.sync_task.urls")),
    url(r"^audits/", include("bkuser_core.api.web.audit.urls")),
    url(r"^fields/", include("bkuser_core.api.web.field.urls")),
    url(r"^profiles/", include("bkuser_core.api.web.profile.urls")),
    url(r"^site/", include("bkuser_core.api.web.site.urls")),
    url(r"^departments/", include("bkuser_core.api.web.department.urls")),
    # url(r"^passwords/", include("bkuser_core.api.web.password.urls")),
    # 通用检索
    url(r"^search/", include("bkuser_core.api.web.search.urls")),
]

# FIXME: 需要检查所有删除的地方, 是不是软删除?
# 重要

# 全局检索
# /api/v2/search/detail/?keyword=aaaa&max_items=40&only_enabled=true
