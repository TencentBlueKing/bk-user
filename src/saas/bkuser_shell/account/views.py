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
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template
from django.template.response import TemplateResponse
from rest_framework import generics

from bkuser_shell.common.error_codes import error_codes


class LoginPageViewSet(generics.RetrieveAPIView):

    permission_classes: list = []

    def get(self, request, *args, **kwargs):
        try:
            return TemplateResponse(request=request, template=get_template("login_success.html"))
        except TemplateDoesNotExist:
            raise error_codes.CANNOT_FIND_TEMPLATE
