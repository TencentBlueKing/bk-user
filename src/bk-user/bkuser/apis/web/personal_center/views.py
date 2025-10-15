# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

import logging
from typing import Dict, List

from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from bkuser.apis.web.personal_center.constants import PersonalCenterFeatureFlag, PhoneOrEmailUpdateRestrictionEnum
from bkuser.apis.web.personal_center.serializers import (
    NaturalUserWithTenantUserListOutputSLZ,
    TenantUserEmailUpdateInputSLZ,
    TenantUserEmailVerificationCodeSendInputSLZ,
    TenantUserExtrasUpdateInputSLZ,
    TenantUserFeatureFlagOutputSLZ,
    TenantUserFieldOutputSLZ,
    TenantUserLanguageUpdateInputSLZ,
    TenantUserLogoUpdateInputSLZ,
    TenantUserMPCallbackInputSLZ,
    TenantUserPasswordRuleRetrieveOutputSLZ,
    TenantUserPasswordUpdateInputSLZ,
    TenantUserPhoneUpdateInputSLZ,
    TenantUserPhoneVerificationCodeSendInputSLZ,
    TenantUserRetrieveOutputSLZ,
    TenantUserTimeZoneUpdateInputSLZ,
    TenantUserWecomCallbackInputSLZ,
    TenantUserWeixinInfoRetrieveOutputSLZ,
    TenantUserWeixinRetrieveToBindInfoOutputSLZ,
)
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.display_name_cache import DisplayNameCacheHandler
from bkuser.apps.tenant.models import TenantUser, TenantUserCustomField, UserBuiltinField
from bkuser.biz.auditor import (
    TenantUserPasswordResetAuditor,
    TenantUserPersonalInfoUpdateAuditor,
    TenantUserWeixinBindAuditor,
)
from bkuser.biz.natural_user import NatureUserHandler
from bkuser.biz.organization import DataSourceUserHandler
from bkuser.biz.password_rule import PasswordRuleHandler
from bkuser.biz.senders import (
    EmailVerificationCodeSender,
    ExceedSendRateLimit,
    PhoneVerificationCodeSender,
)
from bkuser.biz.tenant import TenantUserEmailInfo, TenantUserHandler, TenantUserPhoneInfo
from bkuser.biz.weixin import WeixinConfigProvider
from bkuser.biz.weixin.constants import WeixinTypeEnum
from bkuser.biz.weixin.weixin import MpBindHandler, WecomBindHandler
from bkuser.common.error_codes import error_codes
from bkuser.common.verification_code import (
    EmailVerificationCodeManager,
    GenerateCodeTooFrequently,
    InvalidVerificationCode,
    PhoneVerificationCodeManager,
    RetryLimitExceeded,
    VerificationCodeScene,
)
from bkuser.common.views import ExcludePatchAPIViewMixin

from .mixins import CurrentTenantPhoneOrEmailUpdateRestrictionMixin

logger = logging.getLogger(__name__)


class NaturalUserTenantUserListApi(generics.ListAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]
    pagination_class = None

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="个人中心 - 关联账户列表",
        responses={status.HTTP_200_OK: NaturalUserWithTenantUserListOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        current_tenant_user_id = request.user.username

        # 获取当前登录的租户用户的自然人：两种情况绑定、未绑定，在函数中做处理
        nature_user = NatureUserHandler.get_nature_user_by_tenant_user_id(current_tenant_user_id)

        tenant_users = TenantUser.objects.select_related("data_source_user").filter(
            data_source_user_id__in=nature_user.data_source_user_ids
        )

        # 将当前登录置顶
        # 通过比对租户用户 id, 当等于当前登录用户的租户 id，将其排序到查询集的顶部，否则排序到查询集的底部
        sorted_tenant_users = sorted(tenant_users, key=lambda t: t.id != current_tenant_user_id)

        # 响应数据组装
        nature_user_with_tenant_users_info: Dict = {
            "id": nature_user.id,
            "full_name": nature_user.full_name,
            "tenant_users": [
                {
                    "id": user.id,
                    "username": user.data_source_user.username,
                    "full_name": user.data_source_user.full_name,
                    "logo": user.data_source_user.logo,
                    "tenant": {"id": user.tenant_id, "name": user.tenant.name},
                }
                for user in sorted_tenant_users
            ],
        }

        return Response(NaturalUserWithTenantUserListOutputSLZ(nature_user_with_tenant_users_info).data)


class TenantUserRetrieveApi(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="个人中心 - 关联账户详情",
        responses={status.HTTP_200_OK: TenantUserRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant_user = self.get_object()

        visible_custom_field_names = TenantUserCustomField.objects.filter(
            tenant=tenant_user.tenant, personal_center_visible=True
        ).values_list("name", flat=True)

        slz = TenantUserRetrieveOutputSLZ(
            tenant_user, context={"visible_custom_field_names": visible_custom_field_names}
        )
        return Response(slz.data)


class TenantUserLogoUpdateApi(ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="租户用户更新头像",
        request_body=TenantUserLogoUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = TenantUserLogoUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        tenant_user = self.get_object()
        data_source_user = tenant_user.data_source_user
        data_source_user.logo = data["logo"]
        data_source_user.save(update_fields=["logo", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserPhoneUpdateApi(
    ExcludePatchAPIViewMixin, CurrentTenantPhoneOrEmailUpdateRestrictionMixin, generics.UpdateAPIView
):
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="租户用户更新手机号",
        request_body=TenantUserPhoneUpdateInputSLZ,
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = TenantUserPhoneUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        is_inherited_phone = data["is_inherited_phone"]
        custom_phone = data.get("custom_phone", "")
        custom_phone_country_code = data["custom_phone_country_code"]

        tenant_user = self.get_object()
        restriction = self.get_phone_update_restriction(tenant_user.tenant_id)
        if restriction == PhoneOrEmailUpdateRestrictionEnum.NOT_EDITABLE:
            raise error_codes.TENANT_USER_UPDATE_FAILED.f(_("手机号码不可编辑"))

        if restriction == PhoneOrEmailUpdateRestrictionEnum.NEED_VERIFY and not is_inherited_phone:
            verification_code = data.get("verification_code")
            if not verification_code:
                raise error_codes.INVALID_VERIFICATION_CODE.f(_("验证码不能为空"))

            self._validate_verification_code(
                custom_phone,
                custom_phone_country_code,
                verification_code,
                VerificationCodeScene.UPDATE_PHONE,
            )

        # 【审计】创建租户用户个人信息审计对象并记录变更前的数据
        auditor = TenantUserPersonalInfoUpdateAuditor(request.user.username, tenant_user.tenant_id)
        auditor.pre_record_data_before(tenant_user)

        phone_info = TenantUserPhoneInfo(
            is_inherited_phone=is_inherited_phone,
            custom_phone=custom_phone,
            custom_phone_country_code=custom_phone_country_code,
        )
        TenantUserHandler.update_tenant_user_phone(self.get_object(), phone_info)

        # 【审计】将审计记录保存至数据库
        auditor.record_update_phone(tenant_user)

        # 失效 DisplayName 缓存
        DisplayNameCacheHandler.delete_display_name_cache(tenant_user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _validate_verification_code(
        self, phone: str, phone_country_code: str, code: str, scene: VerificationCodeScene
    ):
        try:
            PhoneVerificationCodeManager(phone, phone_country_code, scene).validate(code)
        except InvalidVerificationCode:
            raise error_codes.INVALID_VERIFICATION_CODE.f(_("验证码错误"))
        except RetryLimitExceeded:
            raise error_codes.VERIFY_VERIFICATION_CODE_FAILED.f(_("超过验证码重试次数"))
        except Exception:
            logger.exception("validate verification code for phone +%s %s failed", phone_country_code, phone)
            raise error_codes.INVALID_VERIFICATION_CODE.f(_("验证码校验失败，请联系管理员处理"))


class TenantUserPhoneVerificationCodeSendApi(CurrentTenantPhoneOrEmailUpdateRestrictionMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="租户修改手机号时发送短信验证码",
        request_body=TenantUserPhoneVerificationCodeSendInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def post(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        restriction = self.get_phone_update_restriction(tenant_user.tenant_id)
        if not restriction == PhoneOrEmailUpdateRestrictionEnum.NEED_VERIFY:
            raise error_codes.SEND_VERIFICATION_CODE_FAILED.f(_("当前租户更新手机号不允许发送验证码"))

        slz = TenantUserPhoneVerificationCodeSendInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        self._send_verification_code_to_user_phone(
            tenant_user, data["phone"], data["phone_country_code"], VerificationCodeScene.UPDATE_PHONE
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _send_verification_code_to_user_phone(
        self, tenant_user: TenantUser, phone: str, phone_country_code: str, scene: VerificationCodeScene
    ):
        """发送短信验证码到指定的租户用户"""

        try:
            code = PhoneVerificationCodeManager(phone, phone_country_code, scene).gen_code()
            logger.info("verification code for phone +%s %s is %s", phone_country_code, phone, code)
        except GenerateCodeTooFrequently:
            raise error_codes.TOO_FREQUENTLY.f(_("发送短信验证码过于频繁，请稍后再试"))

        try:
            PhoneVerificationCodeSender(scene, tenant_user.tenant_id).send(phone, phone_country_code, code)
        except ExceedSendRateLimit:
            raise error_codes.SEND_VERIFICATION_CODE_FAILED.f(_("今日发送验证码次数超过上限，请明天再试"))
        except Exception:
            logger.exception("failed to send verification code to phone +%s %s", phone_country_code, phone)
            raise error_codes.SEND_VERIFICATION_CODE_FAILED.f(_("请联系管理员处理"))


class TenantUserEmailUpdateApi(
    ExcludePatchAPIViewMixin, CurrentTenantPhoneOrEmailUpdateRestrictionMixin, generics.UpdateAPIView
):
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="租户用户更新邮箱",
        request_body=TenantUserEmailUpdateInputSLZ,
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = TenantUserEmailUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        is_inherited_email = data["is_inherited_email"]
        custom_email = data.get("custom_email", "")

        tenant_user = self.get_object()
        restriction = self.get_email_update_restriction(tenant_user.tenant_id)
        if restriction == PhoneOrEmailUpdateRestrictionEnum.NOT_EDITABLE:
            raise error_codes.TENANT_USER_UPDATE_FAILED.f(_("邮箱不可编辑"))

        if restriction == PhoneOrEmailUpdateRestrictionEnum.NEED_VERIFY and not is_inherited_email:
            verification_code = data.get("verification_code")
            if not verification_code:
                raise error_codes.INVALID_VERIFICATION_CODE.f(_("验证码不能为空"))

            self._validate_verification_code(custom_email, verification_code, VerificationCodeScene.UPDATE_EMAIL)

        # 【审计】创建租户用户个人信息审计对象并记录变更前的数据
        auditor = TenantUserPersonalInfoUpdateAuditor(request.user.username, tenant_user.tenant_id)
        auditor.pre_record_data_before(tenant_user)

        email_info = TenantUserEmailInfo(is_inherited_email=is_inherited_email, custom_email=custom_email)
        TenantUserHandler.update_tenant_user_email(self.get_object(), email_info)

        # 【审计】将审计记录保存至数据库
        auditor.record_update_email(tenant_user)

        # 失效 DisplayName 缓存
        DisplayNameCacheHandler.delete_display_name_cache(tenant_user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _validate_verification_code(self, email: str, code: str, scene: VerificationCodeScene):
        try:
            EmailVerificationCodeManager(email, scene).validate(code)
        except InvalidVerificationCode:
            raise error_codes.INVALID_VERIFICATION_CODE.f(_("验证码错误"))
        except RetryLimitExceeded:
            raise error_codes.VERIFY_VERIFICATION_CODE_FAILED.f(_("超过验证码重试次数"))
        except Exception:
            logger.exception("validate verification code for email %s failed", email)
            raise error_codes.INVALID_VERIFICATION_CODE.f(_("验证码校验失败，请联系管理员处理"))


class TenantUserEmailVerificationCodeSendApi(CurrentTenantPhoneOrEmailUpdateRestrictionMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="租户修改邮箱时发送邮箱验证码",
        request_body=TenantUserEmailVerificationCodeSendInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def post(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        restriction = self.get_email_update_restriction(tenant_user.tenant_id)
        if not restriction == PhoneOrEmailUpdateRestrictionEnum.NEED_VERIFY:
            raise error_codes.SEND_VERIFICATION_CODE_FAILED.f(_("当前租户更新邮箱不允许发送验证码"))

        slz = TenantUserEmailVerificationCodeSendInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        self._send_verification_code_to_user_email(tenant_user, data["email"], VerificationCodeScene.UPDATE_EMAIL)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _send_verification_code_to_user_email(self, tenant_user: TenantUser, email: str, scene: VerificationCodeScene):
        """发送邮箱验证码到指定的租户用户"""

        try:
            code = EmailVerificationCodeManager(email, scene).gen_code()
            logger.info("verification code for email %s is %s", email, code)
        except GenerateCodeTooFrequently:
            raise error_codes.TOO_FREQUENTLY.f(_("发送邮箱验证码过于频繁，请稍后再试"))

        try:
            EmailVerificationCodeSender(scene, tenant_user.tenant_id).send(email, code)
        except ExceedSendRateLimit:
            raise error_codes.SEND_VERIFICATION_CODE_FAILED.f(_("今日发送验证码次数超过上限，请明天再试"))
        except Exception:
            logger.exception("failed to send verification code to email %s", email)
            raise error_codes.SEND_VERIFICATION_CODE_FAILED.f(_("请联系管理员处理"))


class TenantUserLanguageUpdateApi(ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="租户用户更新语言",
        request_body=TenantUserLanguageUpdateInputSLZ,
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = TenantUserLanguageUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        tenant_user = self.get_object()
        tenant_user.language = data["language"]
        tenant_user.save(update_fields=["language", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserTimeZoneUpdateApi(ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="租户用户更新时区",
        request_body=TenantUserTimeZoneUpdateInputSLZ,
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        slz = TenantUserTimeZoneUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        tenant_user = self.get_object()
        tenant_user.time_zone = data["time_zone"]
        tenant_user.save(update_fields=["time_zone", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserExtrasUpdateApi(ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="租户用户更新自定义字段",
        request_body=TenantUserExtrasUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        data_source_user = tenant_user.data_source_user

        slz = TenantUserExtrasUpdateInputSLZ(
            data=request.data,
            context={
                "tenant_id": tenant_user.tenant_id,
                "data_source_id": data_source_user.data_source_id,
                "data_source_user_id": data_source_user.id,
            },
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        data_source_user.extras.update(data["extras"])
        data_source_user.save(update_fields=["extras", "updated_at"])

        # 失效 DisplayName 缓存
        DisplayNameCacheHandler.delete_display_name_cache(tenant_user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserFieldListApi(generics.ListAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    pagination_class = None

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="个人中心 - 用户可见字段列表",
        responses={status.HTTP_200_OK: TenantUserFieldOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant_user = self.get_object()

        custom_fields = TenantUserCustomField.objects.filter(tenant=tenant_user.tenant, personal_center_visible=True)
        for f in custom_fields:
            if f.personal_center_editable:
                continue

            selected = tenant_user.data_source_user.extras.get(f.name)
            if not selected:
                f.options = []
                continue

            # 如果该字段是不可编辑的，且是枚举类型，则仅仅返回需要的 options 用于前端展示，避免泄露枚举选项
            if f.data_type == UserFieldDataType.ENUM:
                f.options = [opt for opt in f.options if opt["id"] == selected]
            elif f.data_type == UserFieldDataType.MULTI_ENUM:
                f.options = [opt for opt in f.options if opt["id"] in selected]

        slz = TenantUserFieldOutputSLZ(
            {"builtin_fields": UserBuiltinField.objects.all(), "custom_fields": custom_fields}
        )
        return Response(slz.data)


class TenantUserFeatureFlagListApi(CurrentTenantPhoneOrEmailUpdateRestrictionMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    pagination_class = None

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="个人中心 - 用户功能特性",
        responses={status.HTTP_200_OK: TenantUserFeatureFlagOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        data_source = tenant_user.data_source_user.data_source

        feature_flags = {
            PersonalCenterFeatureFlag.CAN_CHANGE_PASSWORD: bool(
                data_source.is_local and data_source.plugin_config.get("enable_password", False)
            ),
            PersonalCenterFeatureFlag.PHONE_UPDATE_RESTRICTION: self.get_phone_update_restriction(
                tenant_user.tenant_id
            ),
            PersonalCenterFeatureFlag.EMAIL_UPDATE_RESTRICTION: self.get_email_update_restriction(
                tenant_user.tenant_id
            ),
        }
        return Response(TenantUserFeatureFlagOutputSLZ(feature_flags).data)


class TenantUserPasswordUpdateApi(ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="租户用户重置密码",
        request_body=TenantUserPasswordUpdateInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def put(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        data_source_user = tenant_user.data_source_user
        data_source = data_source_user.data_source
        plugin_config = data_source.get_plugin_cfg()

        if not (data_source.is_local and plugin_config.enable_password):
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(
                _("仅可以重置 已经启用密码功能 的 本地数据源 的用户密码")
            )

        slz = TenantUserPasswordUpdateInputSLZ(
            data=request.data,
            context={
                "plugin_config": plugin_config,
                "data_source_user_id": data_source_user.id,
            },
        )
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        new_password = data["new_password"]

        DataSourceUserHandler.update_password(
            data_source_user=data_source_user,
            password=new_password,
            valid_days=plugin_config.password_expire.valid_time,
            operator=request.user.username,
        )
        # 【审计】创建租户用户密码重置操作审计对象
        auditor = TenantUserPasswordResetAuditor(request.user.username, tenant_user.tenant_id)
        # 【审计】将审计记录保存至数据库
        auditor.record(tenant_user.data_source_user, extras={"valid_days": plugin_config.password_expire.valid_time})

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserPasswordRuleRetrieveApi(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="获取租户用户密码规则提示",
        responses={status.HTTP_200_OK: TenantUserPasswordRuleRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        data_source_user = tenant_user.data_source_user
        data_source = data_source_user.data_source

        passwd_rule = PasswordRuleHandler.get_data_source_password_rule(data_source)
        if passwd_rule is None:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(_("该租户用户没有可用的密码规则"))

        return Response(TenantUserPasswordRuleRetrieveOutputSLZ(passwd_rule).data, status=status.HTTP_200_OK)


class TenantUserWeixinInfoRetrieveDestroyApi(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="个人中心 - 查询用户微信 ID",
        responses={status.HTTP_200_OK: TenantUserWeixinInfoRetrieveOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        wx_type = WeixinConfigProvider(tenant_user.tenant_id).get_wx_type()

        data = {"wx_userid": tenant_user.wx_userid, "type": wx_type}
        return Response(TenantUserWeixinInfoRetrieveOutputSLZ(data).data)

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="个人中心 - 删除用户微信 ID",
    )
    def delete(self, request, *args, **kwargs):
        tenant_user = self.get_object()

        if not tenant_user.wx_userid:
            raise error_codes.WEIXIN_ALREADY_UNBOUND.f(_("当前账号未绑定微信"))

        # 【审计】创建微信绑定审计对象并记录变更前的数据
        auditor = TenantUserWeixinBindAuditor(request.user.username, tenant_user.tenant_id)
        auditor.pre_record_data_before(tenant_user)

        # 解绑逻辑
        tenant_user.wx_userid = ""
        tenant_user.save(update_fields=["wx_userid", "updated_at"])

        # 【审计】记录解绑操作
        auditor.record_unbind(tenant_user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserWeixinToBindInfoRetrieveApi(generics.RetrieveAPIView):
    """个人中心 - 统一的绑定接口"""

    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="个人中心 - 微信绑定",
        responses={status.HTTP_200_OK: TenantUserWeixinRetrieveToBindInfoOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant_user = self.get_object()
        if tenant_user.wx_userid:
            raise error_codes.WEIXIN_ALREADY_BOUND.f(_("当前账户已绑定微信"))

        # 获取微信类型
        wx_type = WeixinConfigProvider(tenant_user.tenant_id).get_wx_type()

        url = ""
        if wx_type == WeixinTypeEnum.WeCom.value:
            url = WecomBindHandler(tenant_user).get_authorization_url(request.session)
        elif wx_type == WeixinTypeEnum.MP.value:
            url = MpBindHandler(tenant_user.tenant_id).get_mp_qrcode_url(tenant_user)

        return Response(TenantUserWeixinRetrieveToBindInfoOutputSLZ({"url": url}).data)


class TenantUserWecomCallbackApi(generics.RetrieveAPIView):
    """个人中心 - 企业微信绑定回调接口"""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="个人中心 - 企业微信扫码绑定回调",
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def get(self, request, *args, **kwargs):
        tenant_user = TenantUser.objects.get(id=request.user.username)
        wecom_handler = WecomBindHandler(tenant_user)

        slz = TenantUserWecomCallbackInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data
        code = data["code"]
        state = data["state"]

        if not wecom_handler.check_state(state, request.session):
            raise error_codes.WEIXIN_STATE_INVALID

        wx_userid = wecom_handler.get_wecom_userid(code)

        # 【审计】创建企业微信绑定审计对象并记录变更前的数据
        auditor = TenantUserWeixinBindAuditor(request.user.username, tenant_user.tenant_id)
        auditor.pre_record_data_before(tenant_user)

        # 执行绑定操作
        tenant_user.wx_userid = wx_userid
        tenant_user.save(update_fields=["wx_userid", "updated_at"])

        # 【审计】记录绑定操作
        auditor.record_bind(tenant_user)

        # Note: 这里与前端配合，重新向到绑定成功且 5 秒后自动关闭页面
        return HttpResponseRedirect(redirect_to="/bind-result?status=1")


@method_decorator(csrf_exempt, name="dispatch")
class TenantUserMPCallbackApi(generics.CreateAPIView, generics.RetrieveAPIView):
    """个人中心 - 微信公众号回调接口"""

    # 豁免认证 & 权限
    authentication_classes: List[BaseAuthentication] = []
    permission_classes: List[BasePermission] = []

    def get(self, request, *args, **kwargs):
        slz = TenantUserMPCallbackInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        if not MpBindHandler(self.kwargs["tenant_id"]).check_mp_signature(
            data["signature"], data["timestamp"], data["nonce"]
        ):
            raise error_codes.WEIXIN_SIGN_INVALID.f(_("微信公众号签名验证失败"))

        return HttpResponse(escape(request.query_params.get("echostr")))

    def post(self, request, *args, **kwargs):
        """处理微信公众号回调消息"""
        slz = TenantUserMPCallbackInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        mp_handler = MpBindHandler(self.kwargs["tenant_id"])
        if not mp_handler.check_mp_signature(data["signature"], data["timestamp"], data["nonce"]):
            raise error_codes.WEIXIN_SIGN_INVALID.f(_("微信公众号签名验证失败"))

        tenant_user, wx_userid, response = mp_handler.process_mp_callback_event(request.data)
        # 处理回调事件出错，应该返回空响应作为 fallback，防止微信公众号服务器重复推送
        if not tenant_user:
            return HttpResponse(content="", content_type="application/xml", status=status.HTTP_200_OK)

        # 【审计】创建微信绑定审计对象并记录变更前的数据
        auditor = TenantUserWeixinBindAuditor(tenant_user.id, tenant_user.tenant_id)
        auditor.pre_record_data_before(tenant_user)

        # 执行绑定操作
        tenant_user.wx_userid = wx_userid
        tenant_user.save(update_fields=["wx_userid", "updated_at"])

        # 【审计】记录绑定操作
        auditor.record_bind(tenant_user)

        return HttpResponse(content=response, content_type="application/xml", status=status.HTTP_200_OK)
