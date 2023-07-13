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
from django import forms
from django.contrib import auth


class AuthenticationForm(forms.Form):
    # bk_token format: KH7P4-VSFi_nOEoV3kj0ytcs0uZnGOegIBLV-eM3rw8
    bk_token = forms.CharField()


class LoginMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Login paas when User has logged in calling auth.login
        """
        form = AuthenticationForm(request.COOKIES)

        if form.is_valid():
            bk_token = form.cleaned_data["bk_token"]
            user = auth.authenticate(request=request, bk_token=bk_token)
            if user:
                # Succeed to login, recall self to exit process
                if user.username != request.user.username:
                    auth.login(request, user)
            else:
                auth.logout(request)
        else:
            auth.logout(request)
        return self.get_response(request)
