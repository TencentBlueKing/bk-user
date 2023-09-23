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

from bkuser_core.api.web.category.serializers import CategorySettingOutputSLZ
from bkuser_core.api.web.password.serializers import (
    PasswordListSettingsByTokenInputSLZ,
    PasswordModifyInputSLZ,
    PasswordResetByTokenInputSLZ,
    PasswordResetSendEmailInputSLZ,
    PasswordResetSendSMSInputSLZ,
    PasswordResetSendSMSOutputSLZ,
    PasswordVerifyVerificationCodeInputSLZ,
    PasswordVerifyVerificationCodeOutputSLZ,
)
from bkuser_core.api.web.password.verification_code_handler import ResetPasswordVerificationCodeHandler
from bkuser_core.api.web.utils import (
    get_category,
    get_operator,
    get_profile_by_telephone,
    get_profile_by_username,
    get_token_handler,
    list_setting_metas,
    validate_password,
)
from bkuser_core.audit.constants import OperationType
from bkuser_core.audit.utils import create_general_log
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.error_codes import error_codes
from bkuser_core.profiles.constants import ProfileStatus
from bkuser_core.profiles.exceptions import ProfileEmailEmpty
from bkuser_core.profiles.models import Profile, ProfileTokenHolder
from bkuser_core.profiles.signals import post_profile_update
from bkuser_core.profiles.tasks import send_password_by_email
from bkuser_core.profiles.utils import parse_username_domain
from bkuser_core.user_settings.constants import SettingsEnableNamespaces
from bkuser_core.user_settings.models import Setting

logger = logging.getLogger(__name__)


class PasswordResetSendEmailApi(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        slz = PasswordResetSendEmailInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data
        email = data["email"]

        # 1. get profile by email
        try:
            profile = Profile.objects.get(email=email)
        except Exception:  # pylint: disable=broad-except
            """吞掉异常，保证不能判断出邮箱是否存在"""
            logger.exception("failed to get profile by email<%s>", email)
            return Response(data={})

        # 用户状态校验
        if not profile.is_normal:
            error_msg = (
                "failed to send password via sms."
                "profile is abnormal [profile.id=%s, profile.username=%s, profile.enabled=%s, profile.status=%s]"
            )
            logger.error(
                error_msg, profile.id, f"{profile.username}@{profile.domain}", profile.enabled, profile.status
            )
            raise error_codes.USER_IS_ABNORMAL.f(status=ProfileStatus.get_choice_label(profile.status))

        # FIXME:需要check是否有频率限制，否则会对用户有骚扰 send_password_by_email
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
        slz = PasswordResetByTokenInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data
        token = data["token"]
        pending_password = data["password"]

        token_holder = get_token_handler(token)
        profile = token_holder.profile

        validate_password(profile, pending_password)
        profile.password = make_password(pending_password)
        profile.password_update_time = now()
        profile.save()

        # disabled the token_holder
        token_holder.enabled = False
        token_holder.save()

        # 记录审计日志
        create_general_log(
            operator=request.operator,
            operate_type=OperationType.FORGET_PASSWORD.value,
            operator_obj=profile,
            request=request,
        )

        return Response(status=status.HTTP_200_OK)


class PasswordModifyApi(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        # SaaS 修改密码页面需要登录态, 登录用户即operator
        username = get_operator(request)
        # 注意, 这里的username是带域的
        username, domain = parse_username_domain(username)
        if not domain:
            domain = ProfileCategory.objects.get(default=True).domain
        instance = Profile.objects.get(username=username, domain=domain)

        # 通过context传入操作用户的目录id
        slz = PasswordModifyInputSLZ(data=request.data, context={"category_id": instance.category_id})
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        old_password = data["old_password"]
        new_password = data["new_password"]

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


class PasswordListSettingsByTokenApi(generics.ListAPIView):
    serializer_class = CategorySettingOutputSLZ

    def get(self, request, *args, **kwargs):
        slz = PasswordListSettingsByTokenInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data
        token = data.get("token")

        if token:
            # 根据profile_token 换取目录密码设置
            token_holder = get_token_handler(token)
            profile = token_holder.profile
        else:
            # 兼容登录态的change_password页面获取目录密码配置
            username = get_operator(request)
            username, domain = parse_username_domain(username)
            if not domain:
                domain = ProfileCategory.objects.get(default=True).domain
            try:
                profile = Profile.objects.get(username=username, domain=domain)
            except Profile.DoesNotExist:
                raise error_codes.USER_DOES_NOT_EXIST

        category = get_category(profile.category_id)
        namespace = SettingsEnableNamespaces.PASSWORD.value
        metas = list_setting_metas(category.type, None, namespace)
        settings = Setting.objects.filter(meta__in=metas, category_id=profile.category_id)
        return Response(self.serializer_class(settings, many=True).data)


class PasswordResetSendVerificationCodeApi(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        slz = PasswordResetSendSMSInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data

        input_telephone = data["telephone"]

        # 根据交互设计，和登录一样：只能猜测这里传输的username,还是telephone
        # 存在着username=telephone的情况
        try:
            # 优先过滤username
            username, domain = parse_username_domain(input_telephone)
            if not domain:
                domain = ProfileCategory.objects.get_default().domain
            # filter过滤，判断是否存在，存在则仅有一个
            profile = get_profile_by_username(username, domain)

            # 不存在则才是telephone
            # FIXME: get_profile_by_telephone 和 get_profile_by_username 理论上行为应该一致, 目前不一致, 需要重构
            if not profile:
                profile = get_profile_by_telephone(input_telephone)

            # 用户状态校验
            if not profile.is_normal:
                error_msg = (
                    "failed to send password via sms. "
                    "profile is abnormal [profile.id=%s, profile.username=%s, profile.enabled=%s, profile.status=%s]"
                )

                logger.error(
                    error_msg, profile.id, f"{profile.username}@{profile.domain}", profile.enabled, profile.status
                )
                raise error_codes.USER_IS_ABNORMAL.f(status=ProfileStatus.get_choice_label(profile.status))

        except Profile.DoesNotExist:
            logger.exception(
                "failed to get profile by telephone<%s> or username<%s>", input_telephone, input_telephone
            )
            raise error_codes.USER_DOES_NOT_EXIST

        except Profile.MultipleObjectsReturned:
            logger.exception("this telephone<%s> had bound to multi profiles", input_telephone)
            raise error_codes.TELEPHONE_BOUND_TO_MULTI_PROFILE

        # 生成verification_code_token
        verification_code_token = ResetPasswordVerificationCodeHandler().generate_reset_password_token(profile.id)
        raw_telephone = profile.telephone

        # 用户未绑定手机号，即使用户名就是手机号码
        if not raw_telephone:
            raise error_codes.TELEPHONE_NOT_PROVIDED

        response_data = {
            "verification_code_token": verification_code_token,
            # 加密返回手机号
            "telephone": raw_telephone.replace(raw_telephone[3:7], '****'),
        }

        return Response(PasswordResetSendSMSOutputSLZ(response_data).data)


class PasswordVerifyVerificationCodeApi(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        slz = PasswordVerifyVerificationCodeInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data

        verification_code_handler = ResetPasswordVerificationCodeHandler()

        profile_id = verification_code_handler.verify_verification_code(
            data["verification_code_token"], data["verification_code"]
        )
        profile_token = verification_code_handler.generate_profile_token(profile_id)
        # 前端拿到token，作为query_params，拼接重置页面路由
        response_data = {"token": profile_token.token}
        return Response(PasswordVerifyVerificationCodeOutputSLZ(response_data).data)
