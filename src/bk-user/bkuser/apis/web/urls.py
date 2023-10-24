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
from django.urls import include, path

urlpatterns = [
    # 基础公共，比如当前登录的用户信息，一些常用常量枚举列表等等
    path("basic/", include("bkuser.apis.web.basic.urls")),
    # 租户
    path("tenants/", include("bkuser.apis.web.tenant.urls")),
    path("tenant-organization/", include("bkuser.apis.web.organization.urls")),
    path("data-sources/", include("bkuser.apis.web.data_source.urls")),
    path("data-sources/", include("bkuser.apis.web.data_source_organization.urls")),
    # 个人中心
    path("personal-center/", include("bkuser.apis.web.personal_center.urls")),
    path("tenant-setting/", include("bkuser.apis.web.tenant_setting.urls")),
]
