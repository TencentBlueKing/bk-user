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
import pytz
from django.conf import settings
from django.utils import timezone, translation
from django.utils.deprecation import MiddlewareMixin


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tzname = request.session.get(settings.TIMEZONE_SESSION_KEY)
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()


class LanguageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        language = request.session.get(translation.LANGUAGE_SESSION_KEY)
        if language:
            translation.activate(language)
            request.LANGUAGE_CODE = translation.get_language()


class BKLanguageMiddleware(MiddlewareMixin):
    """
    支持Header为Blueking-Language的语言设置，主要是用于Open API请求，非Web API，因为OpenAPI一般无Cookie
    翻译默认是通过django.middleware.locale.LocaleMiddleware中间件来实现的
    但是LocaleMiddleware中间件里优先对Cookie里语言，再对Header为Accept-Language的值
    这里通过使用Blueking-Language值替换Accept-Language的值来达到设置语言的目的
    Note: BKLanguageMiddleware 必须配置在django.middleware.locale.LocaleMiddleware之前
    """

    BK_LANGUAGE_HEADER = "HTTP_BLUEKING_LANGUAGE"
    LANGUAGE_HEADER = "HTTP_ACCEPT_LANGUAGE"

    def process_request(self, request):
        bk_language = request.META.get(self.BK_LANGUAGE_HEADER)
        if bk_language:
            # Note: bk_language 优先级高于默认的accept_language
            request.META[self.LANGUAGE_HEADER] = bk_language
