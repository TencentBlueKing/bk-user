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
from typing import List

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from bkuser.apis.web.password.constants import TokenRelatedObjType
from bkuser.apis.web.password.senders import (
    EmailResetPasswdTokenSender,
    ExceedSendRateLimit,
    PhoneVerificationCodeSender,
)
from bkuser.apis.web.password.serializers import (
    GenResetPasswordUrlByVerificationCodeInputSLZ,
    GenResetPasswordUrlByVerificationCodeOutputSLZ,
    ListUserByResetPasswordTokenInputSLZ,
    ResetPasswordByTokenInputSLZ,
    SendResetPasswordEmailInputSLZ,
    SendVerificationCodeInputSLZ,
    TenantUserMatchedByTokenOutputSLZ,
)
from bkuser.apis.web.password.tokens import GenerateTokenTooFrequently, UserResetPasswordTokenManager
from bkuser.apps.notification.helpers import gen_reset_password_url
from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.data_source_organization import DataSourceUserHandler
from bkuser.biz.validators import validate_user_new_password
from bkuser.common.error_codes import error_codes
from bkuser.common.verification_code import (
    GenerateCodeTooFrequently,
    InvalidVerificationCode,
    VerificationCodeManager,
    VerificationCodeScene,
)
from bkuser.plugins.constants import DataSourcePluginEnum

logger = logging.getLogger(__name__)


class GetFirstTenantUserMixin:
    """
    根据指定的联系方式，获取租户用户（来源于本地数据源的）

    需要注意的是：同一联系方式可能会匹配到多个用户，该 Mixin 方法只返回第一个，需要注意只能用于通知场景
    """

    def _get_first_tenant_user_by_phone(self, tenant_id: str, phone: str, phone_country_code: str) -> TenantUser:
        # FIXME (su) 补充 status 过滤
        tenant_users = TenantUser.objects.filter_by_phone(tenant_id, phone, phone_country_code).filter(
            data_source_user__data_source__plugin_id=DataSourcePluginEnum.LOCAL
        )

        if not tenant_users.exists():
            raise error_codes.TENANT_USER_NOT_EXIST.f(
                _("手机号码 +{} {} 在租户 {} 中匹配到不到用户").format(phone_country_code, phone, tenant_id),
            )

        return tenant_users.first()

    def _get_first_tenant_user_by_email(self, tenant_id: str, email: str) -> TenantUser:
        # FIXME (su) 补充 status 过滤
        tenant_users = TenantUser.objects.filter_by_email(tenant_id, email).filter(
            data_source_user__data_source__plugin_id=DataSourcePluginEnum.LOCAL
        )

        if not tenant_users.exists():
            raise error_codes.TENANT_USER_NOT_EXIST.f(_("邮箱 {} 在租户 {} 中匹配不到用户").format(email, tenant_id))

        return tenant_users.first()


class SendVerificationCodeApi(GetFirstTenantUserMixin, generics.CreateAPIView):
    # 豁免认证 & 权限
    authentication_classes: List[BaseAuthentication] = []
    permission_classes: List[BasePermission] = []

    @swagger_auto_schema(
        tags=["password"],
        operation_description="发送短信验证码",
        query_serializer=SendVerificationCodeInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def post(self, request, *args, **kwargs):
        slz = SendVerificationCodeInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        tenant_id, phone, phone_country_code = params["tenant_id"], params["phone"], params["phone_country_code"]
        try:
            tenant_user = self._get_first_tenant_user_by_phone(tenant_id, phone, phone_country_code)
        except Exception:
            if settings.ALLOW_RAISE_ERROR_TO_USER_WHEN_RESET_PASSWORD:
                raise

            logger.warning(
                "failed to get tenant user by phone +%s %s in tenant %s", phone_country_code, phone, tenant_id
            )
            return Response(status=status.HTTP_204_NO_CONTENT)

        self._send_verification_code_to_user_phone(tenant_user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _send_verification_code_to_user_phone(self, tenant_user: TenantUser):
        """发送短信验证码到指定的租户用户"""
        phone, phone_country_code = tenant_user.phone_info
        try:
            code = VerificationCodeManager(phone, phone_country_code, VerificationCodeScene.RESET_PASSWORD).gen_code()
        except GenerateCodeTooFrequently:
            raise error_codes.TOO_FREQUENTLY.f(_("发送短信验证码过于频繁，请稍后再试"))

        try:
            PhoneVerificationCodeSender(VerificationCodeScene.RESET_PASSWORD).send(tenant_user, code)
        except ExceedSendRateLimit:
            raise error_codes.SEND_VERIFICATION_CODE_FAILED.f(_("今日发送验证码次数超过上限，请明天再试"))
        except Exception:
            logger.exception("failed to send verification code to user %s", tenant_user.id)
            raise error_codes.SEND_VERIFICATION_CODE_FAILED.f(_("请联系管理员处理"))


class GenResetPasswordUrlByVerificationCodeApi(GetFirstTenantUserMixin, generics.CreateAPIView):
    # 豁免认证 & 权限
    authentication_classes: List[BaseAuthentication] = []
    permission_classes: List[BasePermission] = []

    @swagger_auto_schema(
        tags=["password"],
        operation_description="通过短信验证码获取重置密码链接",
        query_serializer=GenResetPasswordUrlByVerificationCodeInputSLZ(),
        responses={status.HTTP_200_OK: GenResetPasswordUrlByVerificationCodeOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        slz = GenResetPasswordUrlByVerificationCodeInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        tenant_id = params["tenant_id"]
        phone, phone_country_code = params["phone"], params["phone_country_code"]
        # 1. 找到匹配的租户用户
        try:
            tenant_user = self._get_first_tenant_user_by_phone(tenant_id, phone, phone_country_code)
        except Exception:
            if settings.ALLOW_RAISE_ERROR_TO_USER_WHEN_RESET_PASSWORD:
                raise

            logger.warning(
                "failed to get tenant user by phone +%s %s in tenant %s", phone_country_code, phone, tenant_id
            )
            return Response(status=status.HTTP_204_NO_CONTENT)

        # 2. 校验验证码是否正确
        self._validate_verification_code(phone, phone_country_code, params["verification_code"])
        # 3. 获取重置密码链接
        url = self._gen_reset_password_url(tenant_user)

        return Response(GenResetPasswordUrlByVerificationCodeOutputSLZ({"reset_password_url": url}).data)

    def _validate_verification_code(self, phone: str, phone_country_code: str, code: str):
        try:
            VerificationCodeManager(phone, phone_country_code, VerificationCodeScene.RESET_PASSWORD).validate(code)
        except InvalidVerificationCode:
            raise error_codes.INVALID_VERIFICATION_CODE.f(_("验证码错误"))
        except Exception:
            logger.exception("validate verification code for phone +%s %s failed", phone_country_code, phone)
            raise error_codes.SEND_VERIFICATION_CODE_FAILED.f(_("验证码校验失败，请联系管理员处理"))

    def _gen_reset_password_url(self, tenant_user: TenantUser) -> str:
        try:
            token = UserResetPasswordTokenManager().gen_token(tenant_user, TokenRelatedObjType.PHONE)
        except GenerateTokenTooFrequently:
            raise error_codes.TOO_FREQUENTLY.f(_("请稍后再试"))

        return gen_reset_password_url(token)


class SendResetPasswordEmailApi(GetFirstTenantUserMixin, generics.CreateAPIView):
    # 豁免认证 & 权限
    authentication_classes: List[BaseAuthentication] = []
    permission_classes: List[BasePermission] = []

    @swagger_auto_schema(
        tags=["password"],
        operation_description="发送重置密码链接到用户邮箱",
        query_serializer=SendResetPasswordEmailInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def post(self, request, *args, **kwargs):
        slz = SendResetPasswordEmailInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        try:
            tenant_user = self._get_first_tenant_user_by_email(params["tenant_id"], params["email"])
        except Exception:
            if settings.ALLOW_RAISE_ERROR_TO_USER_WHEN_RESET_PASSWORD:
                raise

            logger.warning("failed to get tenant user by email %s in tenant %s", params["email"], params["tenant_id"])
            return Response(status=status.HTTP_204_NO_CONTENT)

        self._gen_and_send_reset_password_url(tenant_user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _gen_and_send_reset_password_url(self, tenant_user: TenantUser) -> None:
        try:
            token = UserResetPasswordTokenManager().gen_token(tenant_user, TokenRelatedObjType.EMAIL)
        except GenerateTokenTooFrequently:
            raise error_codes.TOO_FREQUENTLY.f(_("请稍后再试"))

        try:
            EmailResetPasswdTokenSender().send(tenant_user, token)
        except ExceedSendRateLimit:
            raise error_codes.SEND_RESET_PASSWORD_EMAIL_FAILED.f(_("今日发送次数超过上限，请明天再试"))
        except Exception:
            logger.exception("failed to send reset password url to user %s", tenant_user.id)
            raise error_codes.SEND_RESET_PASSWORD_EMAIL_FAILED.f(_("请联系管理员处理"))


class ListUsersByResetPasswordTokenApi(generics.ListAPIView):
    # 豁免认证 & 权限
    authentication_classes: List[BaseAuthentication] = []
    permission_classes: List[BasePermission] = []
    pagination_class = None

    @swagger_auto_schema(
        tags=["password"],
        operation_description="根据 Token 获取可重置密码的租户用户列表",
        query_serializer=ListUserByResetPasswordTokenInputSLZ(),
        responses={status.HTTP_200_OK: TenantUserMatchedByTokenOutputSLZ(many=True)},
    )
    def get(self, request, *args, **kwargs):
        slz = ListUserByResetPasswordTokenInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        # 只是查询租户用户列表，不应该使得令牌失效，否则后续无法进行校验
        tenant_users = UserResetPasswordTokenManager().list_users_by_token(params["token"])
        return Response(TenantUserMatchedByTokenOutputSLZ(tenant_users, many=True).data)


class ResetPasswordByTokenApi(generics.CreateAPIView):
    # 豁免认证 & 权限
    authentication_classes: List[BaseAuthentication] = []
    permission_classes: List[BasePermission] = []

    @swagger_auto_schema(
        tags=["password"],
        operation_description="根据 Token 重置密码",
        query_serializer=ResetPasswordByTokenInputSLZ(),
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def post(self, request, *args, **kwargs):
        slz = ResetPasswordByTokenInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data
        token, password = params["token"], params["password"]

        token_mgr = UserResetPasswordTokenManager()
        tenant_user = token_mgr.list_users_by_token(token).filter(id=params["tenant_user_id"]).first()
        if not tenant_user:
            raise error_codes.TENANT_USER_NOT_EXIST.f(_("租户用户不存在"))

        data_source_user = tenant_user.data_source_user
        plugin_cfg = data_source_user.data_source.get_plugin_cfg()
        validate_user_new_password(password, data_source_user.id, plugin_cfg)

        DataSourceUserHandler.update_password(
            data_source_user=data_source_user,
            password=password,
            valid_days=plugin_cfg.password_expire.valid_time,
            operator="AnonymousByResetToken",
        )
        # 成功修改完用户密码后，需要及时禁用 Token
        token_mgr.disable_token(token)

        return Response(status=status.HTTP_204_NO_CONTENT)
