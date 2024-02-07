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

from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from bkuser.apis.web.password.serializers import (
    ResetPasswordByVerificationCodeInputSLZ,
    SendResetPasswordVerificationCodeInputSLZ,
    SendResetPasswordVerificationCodeOutputSLZ,
)
from bkuser.apps.notification.constants import NotificationMethod, NotificationScene, VerificationCodeScene
from bkuser.apps.notification.exceptions import (
    ExceedSendVerificationCodeLimit,
    ExceedVerificationCodeRetries,
    InvalidVerificationCode,
)
from bkuser.apps.notification.tasks import send_reset_password_to_user
from bkuser.apps.notification.verification_code import VerificationCodeManager
from bkuser.apps.tenant.models import TenantUser
from bkuser.biz.data_source_organization import DataSourceUserHandler
from bkuser.common.error_codes import error_codes
from bkuser.common.passwd import PasswordGenerator

logger = logging.getLogger(__name__)


class SendResetPasswordVerificationCodeApi(generics.CreateAPIView):
    # 豁免认证 & 权限
    authentication_classes = None
    permission_classes = None

    @swagger_auto_schema(
        tags=["password"],
        operation_description="发送重置密码验证码",
        query_serializer=SendResetPasswordVerificationCodeInputSLZ(),
        responses={status.HTTP_200_OK: SendResetPasswordVerificationCodeOutputSLZ()},
    )
    def post(self, request, *args, **kwargs):
        slz = SendResetPasswordVerificationCodeInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        # 1. 根据用户提交的邮箱 / 手机号码找到租户用户
        if email := params.get("email"):
            tenant_user = self._get_tenant_user_by_email(params["tenant_id"], email)
            method = NotificationMethod.EMAIL
        else:
            tenant_user = self._get_tenant_user_by_phone(
                params["tenant_id"], params["phone"], params["phone_country_code"]
            )
            method = NotificationMethod.SMS

        # 2. 检查该租户用户关联的数据源用户，是否属于本地数据源
        if not tenant_user.data_source_user.data_source.is_local:
            raise error_codes.CANNOT_RESET_DATA_SOURCE_USER_PASSWORD.f(_("仅本地数据源用户可重置密码"))

        # 3. 通过指定的途径发送验证码
        self._send_verification_code_to_user(tenant_user, method)

        # 4. 返回租户用户 ID 用于后续流程
        return Response(SendResetPasswordVerificationCodeOutputSLZ(instance={"user_id": tenant_user.id}).data)

    def _get_tenant_user_by_email(self, tenant_id: str, email: str) -> TenantUser:
        # FIXME (su) 补充 status 过滤
        tenant_users = TenantUser.objects.filter(tenant_id=tenant_id).filter(
            Q(is_inherited_email=False, custom_email=email) | Q(is_inherited_email=True, data_source_user__email=email)
        )
        if not tenant_users.exists():
            raise error_codes.TENANT_USER_NOT_EXIST.f(_("邮箱 {} 在租户 {} 中匹配不到用户").format(email, tenant_id))

        if tenant_users.count() > 1:
            raise error_codes.MATCH_MORE_THAN_ONE_USER.f(
                _("邮箱 {} 在租户 {} 中匹配到多个用户").format(email, tenant_id)
            )

        return tenant_users.first()

    def _get_tenant_user_by_phone(self, tenant_id: str, phone: str, phone_country_code: str) -> TenantUser:
        # FIXME (su) 补充 status 过滤
        tenant_users = TenantUser.objects.filter(tenant_id=tenant_id).filter(
            Q(
                is_inherited_email=False,
                custom_phone=phone,
                custom_phone_country_code=phone_country_code,
            )
            | Q(
                is_inherited_email=True,
                data_source_user__phone=phone,
                data_source_user__phone_country_code=phone_country_code,
            )
        )
        if not tenant_users.exists():
            raise error_codes.MATCH_MORE_THAN_ONE_USER.f(
                _("手机号码 +{} {} 在租户 {} 中匹配到不到用户").format(phone_country_code, phone, tenant_id),
            )

        if tenant_users.count() > 1:
            raise error_codes.MATCH_MORE_THAN_ONE_USER.f(
                _("手机号码 +{} {} 在租户 {} 中匹配到多个用户").format(phone_country_code, phone, tenant_id),
            )

        return tenant_users.first()

    def _send_verification_code_to_user(self, tenant_user: TenantUser, method: NotificationMethod):
        """发送验证码到指定的租户用户"""
        try:
            VerificationCodeManager(tenant_user, VerificationCodeScene.RESET_PASSWORD).send(method)
        except ExceedSendVerificationCodeLimit:
            raise error_codes.SEND_VERIFICATION_CODE_FAILED.f(_("今日发送验证码次数超过上限，请明天再试"))
        except Exception:
            logger.exception("failed to send verification code to user %s", tenant_user.id)
            raise error_codes.SEND_VERIFICATION_CODE_FAILED.f(_("请联系管理员处理"))


class ResetPasswordByVerificationCodeApi(generics.CreateAPIView):
    # 豁免认证 & 权限
    authentication_classes = None
    permission_classes = None

    @swagger_auto_schema(
        tags=["password"],
        operation_description="使用验证码重置租户密码",
        query_serializer=ResetPasswordByVerificationCodeInputSLZ(),
    )
    def post(self, request, *args, **kwargs):
        slz = ResetPasswordByVerificationCodeInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        tenant_user_id, verification_code = params["user_id"], params["verification_code"]
        # 1. 寻找指定的租户用户
        # FIXME (su) 补充 status 过滤
        tenant_user = TenantUser.objects.filter(id=tenant_user_id).first()
        if not tenant_user:
            raise error_codes.TENANT_USER_NOT_EXIST.f(_("ID 为 {} 的用户不存在").format(tenant_user_id))

        # 2. 检查该租户用户是否允许重置密码
        if not tenant_user.data_source_user.data_source.is_local:
            raise error_codes.CANNOT_RESET_DATA_SOURCE_USER_PASSWORD.f(_("仅本地数据源用户可重置密码"))

        # 3. 校验验证码是否属于该租户用户且有效
        self._validate_verification_code(tenant_user, verification_code)

        # 4. 根据数据源配置重置密码
        self._reset_password_by_cfg_and_send_notification(tenant_user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _validate_verification_code(self, tenant_user, verification_code):
        try:
            VerificationCodeManager(tenant_user, VerificationCodeScene.RESET_PASSWORD).validate(verification_code)
        except ExceedVerificationCodeRetries:
            raise error_codes.INVALID_VERIFICATION_CODE.f(_("试错次数超过上限导致验证码失效，需重新发送"))
        except InvalidVerificationCode:
            raise error_codes.INVALID_VERIFICATION_CODE.f(_("请输入正确的验证码"))
        except Exception:
            logger.exception("failed to validate verification code to user %s", tenant_user.id)
            raise error_codes.SEND_VERIFICATION_CODE_FAILED.f(_("验证码校验失败，请联系管理员处理"))

    def _reset_password_by_cfg_and_send_notification(self, tenant_user):
        data_source_user = tenant_user.data_source_user
        plugin_cfg = data_source_user.data_source.get_plugin_cfg()
        password = PasswordGenerator(plugin_cfg.password_rule.to_rule()).generate()

        DataSourceUserHandler.update_password(
            data_source_user=data_source_user,
            password=password,
            valid_days=plugin_cfg.password_rule.valid_time,
            operator="AnonymousByVerificationCode",
        )

        # 发送新密码通知到用户
        # FIXME (su) 这里有一个讨论点，通知到的是数据源用户的数据源所在租户的关联的租户用户，不一定是指定的租户用户
        send_reset_password_to_user.delay(data_source_user.id, NotificationScene.RESET_PASSWORD, password)
