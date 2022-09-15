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

import logging

from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import PasswordModifySerializer, PasswordResetByTokenSerializer, PasswordResetSendEmailSerializer
from bkuser_core.api.web.utils import get_username, validate_password
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.error_codes import error_codes
from bkuser_core.profiles.exceptions import ProfileEmailEmpty
from bkuser_core.profiles.models import Profile, ProfileTokenHolder
from bkuser_core.profiles.signals import post_profile_update
from bkuser_core.profiles.tasks import send_password_by_email
from bkuser_core.profiles.utils import parse_username_domain

logger = logging.getLogger(__name__)


class PasswordResetSendEmailApi(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        email = data["email"]

        # 1. get profile by email
        try:
            profile = Profile.objects.get(email=email)
        except Exception:  # pylint: disable=broad-except
            """吞掉异常，保证不能判断出邮箱是否存在"""
            logger.exception("failed to get profile by email<%s>", email)
            return Response(data={})

        token_holder = ProfileTokenHolder.objects.create(profile=profile)
        try:
            send_password_by_email.delay(profile_id=profile.id, token=token_holder.token, init=False)
        except ProfileEmailEmpty:
            raise error_codes.EMAIL_NOT_PROVIDED
        except Exception:  # pylint: disable=broad-except
            logger.exception(
                "failed to send password via email. [profile.id=%s, profile.username=%s]",
                profile.id,
                profile.username,
            )

        return Response(status=status.HTTP_200_OK)


class PasswordResetByTokenApi(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetByTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        token = data["token"]
        pending_password = data["password"]

        try:
            token_holder = ProfileTokenHolder.objects.get(token=token, enabled=True)
        except ProfileTokenHolder.DoesNotExist:
            logger.info("token<%s> not exist in db", token)
            raise error_codes.CANNOT_GET_TOKEN_HOLDER

        if token_holder.expired:
            raise error_codes.PROFILE_TOKEN_EXPIRED

        # FIXME: 记录审计日志 OperationType.FORGET_PASSWORD.value
        profile = token_holder.profile
        validate_password(profile, pending_password)
        profile.password = make_password(pending_password)
        profile.password_update_time = now()
        profile.save()

        return Response(status=status.HTTP_200_OK)


class PasswordModifyApi(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        serializer = PasswordModifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        old_password = data["old_password"]
        new_password = data["new_password"]

        # SaaS 修改密码页面需要登录态, 登录用户即operator
        username = get_username(request)

        # 注意, 这里的username是带域的
        username, domain = parse_username_domain(username)
        if not domain:
            domain = ProfileCategory.objects.get(default=True).domain

        instance = Profile.objects.get(username=username, domain=domain)

        # 1. check old match
        if not instance.check_password(old_password):
            raise error_codes.PASSWORD_ERROR

        # 2. validate new
        validate_password(instance, new_password)

        instance.password = make_password(new_password)
        instance.password_update_time = now()
        instance.save(update_fields=["password", "password_update_time", "update_time"])

        modify_summary = {
            "request": request,
            "should_notify": True,
            "raw_password": new_password,
        }
        post_profile_update.send(
            sender=self,
            instance=instance,
            operator=request.operator,
            extra_values=modify_summary,
        )
        return Response(status=status.HTTP_200_OK)
