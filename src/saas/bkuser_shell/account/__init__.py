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
from django.utils.module_loading import import_string

from bkuser_shell.account.conf import AUTH_USER_MODEL, ConfFixture


def load_backend(backend):
    path = "bkuser_shell.account.components.{backend}".format(backend=backend)
    return import_string(path)


def get_user_model():
    """
    返回平台对应版本 User Proxy Model
    """
    return load_backend(ConfFixture.USER_MODEL)


def get_bk_login_ticket(request):
    form_cls = "AuthenticationForm"
    context = [request.COOKIES, request.GET]

    authentication_form_cls = load_backend("forms.{}".format(form_cls))

    for form in (authentication_form_cls(c) for c in context):
        if form.is_valid():
            return form.cleaned_data

    return {}


if AUTH_USER_MODEL == settings.AUTH_USER_MODEL:
    from django.contrib import auth

    auth.get_user_model = get_user_model
