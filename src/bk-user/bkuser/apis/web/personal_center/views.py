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
from typing import Dict

from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
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
    TenantUserPasswordUpdateInputSLZ,
    TenantUserPhoneUpdateInputSLZ,
    TenantUserPhoneVerificationCodeSendInputSLZ,
    TenantUserRetrieveOutputSLZ,
    TenantUserTimeZoneUpdateInputSLZ,
)
from bkuser.apps.audit.constants import ObjectTypeEnum, OperationEnum
from bkuser.apps.audit.recorder import add_audit_record
from bkuser.apps.permission.constants import PermAction
from bkuser.apps.permission.permissions import perm_class
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.models import TenantUser, TenantUserCustomField, UserBuiltinField
from bkuser.biz.natural_user import NatureUserHandler
from bkuser.biz.organization import DataSourceUserHandler
from bkuser.biz.senders import (
    EmailVerificationCodeSender,
    ExceedSendRateLimit,
    PhoneVerificationCodeSender,
)
from bkuser.biz.tenant import TenantUserEmailInfo, TenantUserHandler, TenantUserPhoneInfo
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
    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="个人中心-关联账户列表",
        responses={status.HTTP_200_OK: NaturalUserWithTenantUserListOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        current_tenant_user_id = request.user.username

        # 获取当前登录的租户用户的自然人:两种情况绑定、未绑定，在函数中做处理
        nature_user = NatureUserHandler.get_nature_user_by_tenant_user_id(current_tenant_user_id)

        tenant_users = TenantUser.objects.select_related("data_source_user").filter(
            data_source_user_id__in=nature_user.data_source_user_ids
        )

        # 将当前登录置顶
        # 通过比对租户用户id, 当等于当前登录用户的租户id，将其排序到查询集的顶部, 否则排序到查询集的底部
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
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="个人中心-关联账户详情",
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
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

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
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

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

        # 【审计】记录更改前数据
        data_before = {
            "is_inherited_phone": tenant_user.is_inherited_phone,
            "custom_phone": tenant_user.custom_phone,
            "custom_phone_country_code": tenant_user.custom_phone_country_code,
        }

        phone_info = TenantUserPhoneInfo(
            is_inherited_phone=is_inherited_phone,
            custom_phone=custom_phone,
            custom_phone_country_code=custom_phone_country_code,
        )
        TenantUserHandler.update_tenant_user_phone(self.get_object(), phone_info)

        # 审计记录
        add_audit_record(
            operator=request.user.username,
            tenant_id=tenant_user.tenant_id,
            operation=OperationEnum.MODIFY_USER_PHONE,
            object_type=ObjectTypeEnum.USER,
            object_id=tenant_user.id,
            extras={"data_before": data_before},
        )

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
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

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

        tenant_user.custom_phone = data["phone"]
        tenant_user.custom_phone_country_code = data["phone_country_code"]
        self._send_verification_code_to_user_phone(tenant_user, VerificationCodeScene.UPDATE_PHONE)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _send_verification_code_to_user_phone(self, tenant_user: TenantUser, scene: VerificationCodeScene):
        """发送短信验证码到指定的租户用户"""
        phone, phone_country_code = tenant_user.custom_phone, tenant_user.custom_phone_country_code

        try:
            code = PhoneVerificationCodeManager(phone, phone_country_code, scene).gen_code()
            logger.info("verification code for phone +%s %s is %s", phone_country_code, phone, code)
        except GenerateCodeTooFrequently:
            raise error_codes.TOO_FREQUENTLY.f(_("发送短信验证码过于频繁，请稍后再试"))

        # FIXME: ESB只支持根据 username 发送，这里修改手机号并没有保存，发送的还是旧的，后续修复
        try:
            PhoneVerificationCodeSender(scene).send(tenant_user, code)
        except ExceedSendRateLimit:
            raise error_codes.SEND_VERIFICATION_CODE_FAILED.f(_("今日发送验证码次数超过上限，请明天再试"))
        except Exception:
            logger.exception("failed to send verification code to user %s", tenant_user.id)
            raise error_codes.SEND_VERIFICATION_CODE_FAILED.f(_("请联系管理员处理"))


class TenantUserEmailUpdateApi(
    ExcludePatchAPIViewMixin, CurrentTenantPhoneOrEmailUpdateRestrictionMixin, generics.UpdateAPIView
):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

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

        # 【审计】记录更改前数据
        data_before = {
            "is_inherited_email": tenant_user.is_inherited_email,
            "custom_email": tenant_user.custom_email,
        }

        email_info = TenantUserEmailInfo(is_inherited_email=is_inherited_email, custom_email=custom_email)
        TenantUserHandler.update_tenant_user_email(self.get_object(), email_info)

        # 审计记录
        add_audit_record(
            operator=request.user.username,
            tenant_id=tenant_user.tenant_id,
            operation=OperationEnum.MODIFY_USER_EMAIL,
            object_type=ObjectTypeEnum.USER,
            object_id=tenant_user.id,
            extras={"data_before": data_before},
        )

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
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

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
        email = slz.validated_data["email"]

        tenant_user.custom_email = email
        self._send_verification_code_to_user_email(tenant_user, VerificationCodeScene.UPDATE_EMAIL)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _send_verification_code_to_user_email(self, tenant_user: TenantUser, scene: VerificationCodeScene):
        """发送邮箱验证码到指定的租户用户"""
        email = tenant_user.custom_email

        try:
            code = EmailVerificationCodeManager(email, scene).gen_code()
            logger.info("verification code for email %s is %s", email, code)
        except GenerateCodeTooFrequently:
            raise error_codes.TOO_FREQUENTLY.f(_("发送邮箱验证码过于频繁，请稍后再试"))

        try:
            EmailVerificationCodeSender(scene).send(tenant_user, code)
        except ExceedSendRateLimit:
            raise error_codes.SEND_VERIFICATION_CODE_FAILED.f(_("今日发送验证码次数超过上限，请明天再试"))
        except Exception:
            logger.exception("failed to send verification code to user %s", tenant_user.id)
            raise error_codes.SEND_VERIFICATION_CODE_FAILED.f(_("请联系管理员处理"))


class TenantUserLanguageUpdateApi(ExcludePatchAPIViewMixin, generics.UpdateAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

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
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

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
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

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
        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantUserFieldListApi(generics.ListAPIView):
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="个人中心-用户可见字段列表",
        responses={status.HTTP_200_OK: TenantUserFieldOutputSLZ()},
    )
    def get(self, request, *args, **kwargs):
        tenant_user = self.get_object()

        custom_fields = TenantUserCustomField.objects.filter(tenant=tenant_user.tenant, personal_center_visible=True)
        for f in custom_fields:
            if f.personal_center_editable:
                continue

            selected = tenant_user.data_source_user.extras.get(f.name)
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
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    pagination_class = None
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

    @swagger_auto_schema(
        tags=["personal_center"],
        operation_description="个人中心-用户功能特性",
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
    queryset = TenantUser.objects.all()
    lookup_url_kwarg = "id"
    permission_classes = [IsAuthenticated, perm_class(PermAction.USE_PLATFORM)]

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

        # 审计记录
        add_audit_record(
            operator=request.user.username,
            tenant_id=tenant_user.tenant_id,
            operation=OperationEnum.MODIFY_USER_PASSWORD,
            object_type=ObjectTypeEnum.USER,
            object_id=tenant_user.id,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
