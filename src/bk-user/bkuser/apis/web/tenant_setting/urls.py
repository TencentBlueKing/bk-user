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
from django.urls import path

from . import views

urlpatterns = [
    path("<str:tenant_id>/fields/", views.UserFieldListApi.as_view(), name="tenant_setting_fields.list"),
    path(
        "<str:tenant_id>/custom_fields/",
        views.UserCustomFieldCreateApi.as_view(),
        name="tenant_setting_custom_fields.create",
    ),
    path(
        "custom_fields/<int:id>/",
        views.UserCustomFieldUpdateDeleteApi.as_view(),
        name="tenant_setting_custom_fields.update_delete",
    ),
]
