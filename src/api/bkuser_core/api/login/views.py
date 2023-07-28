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
import datetime
import functools
import logging
from collections import defaultdict
from operator import or_

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.response import Response

from bkuser_core.api.login.serializers import (
    LoginBatchQuerySerializer,
    LoginBatchResponseSerializer,
    LoginUpsertSerializer,
    ProfileLoginSerializer,
    ProfileSerializer,
)
from bkuser_core.audit.constants import LogInFailReason
from bkuser_core.audit.utils import create_profile_log
from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.loader import get_plugin_by_category
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.cache import clear_cache_if_succeed
from bkuser_core.common.error_codes import error_codes
from bkuser_core.profiles.constants import ProfileStatus, StaffStatus
from bkuser_core.profiles.models import Profile, ProfileTokenHolder
from bkuser_core.profiles.utils import align_country_iso_code, make_passwd_reset_url_by_token, parse_username_domain
from bkuser_core.profiles.validators import validate_username
from bkuser_core.user_settings.loader import ConfigProvider

logger = logging.getLogger(__name__)


class ProfileLoginViewSet(viewsets.ViewSet):
    """登陆均为兼容代码"""

    @swagger_auto_schema(
        request_body=ProfileLoginSerializer,
        responses={"200": ProfileSerializer()},
    )
    def login(self, request):
        """登录信息校验"""
        serializer = ProfileLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")
        domain = serializer.validated_data.get("domain", None)

        logger.debug("do login check, username<%s>, domain=<%s>", username, domain)
        # 无指定 domain 时, 选择默认域
        if not domain:
            category = ProfileCategory.objects.get_default()
        else:
            try:
                category = ProfileCategory.objects.get(domain=domain)
            except ProfileCategory.DoesNotExist:
                raise error_codes.DOMAIN_UNKNOWN

            # 限制异常状态目录下人员登录
            if category.inactive:
                raise error_codes.CATEGORY_NOT_ENABLED
            if category.is_deleted:
                logger.info("Category<%s-%s> has been deleted", category.id, category.domain)
                raise error_codes.DOMAIN_UNKNOWN

        logger.debug(
            "do login check, will check in category<%s-%s-%s>", category.type, category.display_name, category.id
        )

        message_detail = (
            f"username={username}, domain={domain} in category<{category.type}-{category.display_name}-{category.id}>"
        )

        # 这里不检查具体的用户名格式，只判断是否能够获取到对应用户
        try:
            profile = Profile.objects.get(
                Q(email=username) | Q(telephone=username) | Q(username=username),
                domain=category.domain,
            )
        except Profile.DoesNotExist:
            logger.info("login check, can't find the %s", message_detail)
            # NOTE: 这里不能使用 USER_DOES_NOT_EXIST, 安全问题
            raise error_codes.PASSWORD_ERROR
        except MultipleObjectsReturned:
            logger.info("login check, find multiple profiles via %s", message_detail)
            # NOTE: 安全原因, 不能返回账户状态
            raise error_codes.PASSWORD_ERROR
            # raise error_codes.USER_EXIST_MANY

        time_aware_now = now()
        config_loader = ConfigProvider(category_id=category.id)
        # 由于安全检测等原因，取消原先对admin用户的检查豁免
        if category.type in [CategoryType.LOCAL.value]:

            # 判断账户状态
            if profile.status in [
                ProfileStatus.DISABLED.value,
                ProfileStatus.DELETED.value,
            ]:
                if profile.status == ProfileStatus.DISABLED.value:
                    failed_reason = LogInFailReason.DISABLED_USER.value
                else:
                    failed_reason = LogInFailReason.DELETED_USER.value
                create_profile_log(
                    profile=profile,
                    operation="LogIn",
                    request=request,
                    params={"is_success": False, "reason": failed_reason},
                )
                logger.info("login check, profile<%s> of %s is %s", profile.username, message_detail, profile.status)
                raise error_codes.PASSWORD_ERROR
                # NOTE: 安全原因, 不能返回账户状态
                # if profile.status == ProfileStatus.DISABLED.value:
                #     raise error_codes.USER_IS_DISABLED
                # else:
                #     raise error_codes.USER_IS_DELETED
            elif profile.status == ProfileStatus.LOCKED.value:
                create_profile_log(
                    profile=profile,
                    operation="LogIn",
                    request=request,
                    params={"is_success": False, "reason": LogInFailReason.LOCKED_USER.value},
                )
                logger.info("login check, profile<%s> of %s is locked", profile.username, message_detail)
                raise error_codes.PASSWORD_ERROR
                # NOTE: 安全原因, 不能返回账户状态
                # raise error_codes.USER_IS_LOCKED
            elif profile.staff_status == StaffStatus.OUT.value:
                create_profile_log(
                    profile=profile,
                    operation="LogIn",
                    request=request,
                    params={"is_success": False, "reason": LogInFailReason.RESIGNED_USER.value},
                )
                logger.info("login check, profile<%s> of %s is resigned", profile.username, message_detail)
                raise error_codes.PASSWORD_ERROR
                # NOTE: 安全原因, 不能返回账户状态
                # raise error_codes.USER_IS_RESIGNED

            # 获取密码配置
            auto_unlock_seconds = int(config_loader["auto_unlock_seconds"])
            max_trail_times = int(config_loader["max_trail_times"])

            # 错误登录次数校验
            if profile.bad_check_cnt >= max_trail_times > 0:
                from_last_check_seconds = (time_aware_now - profile.latest_check_time).total_seconds()
                retry_after_wait = int(auto_unlock_seconds - from_last_check_seconds)

                if retry_after_wait > 0:
                    create_profile_log(
                        profile=profile,
                        operation="LogIn",
                        request=request,
                        params={"is_success": False, "reason": LogInFailReason.TOO_MANY_FAILURE.value},
                    )

                    logger.info(f"用户<{profile}> 登录失败错误过多，已被锁定，请 {retry_after_wait}s 后再试")
                    # 当密码输入错误时，不暴露不同的信息，避免用户名爆破
                    logger.info(
                        "login check, profile<%s> of %s entered wrong password too many times",
                        profile.username,
                        message_detail,
                    )
                    # NOTE: 安全原因, 不能返回账户状态
                    raise error_codes.PASSWORD_ERROR

        try:
            login_class = get_plugin_by_category(category).login_handler_cls
        except Exception:
            logger.exception(
                "login check, category<%s-%s-%s> load login handler failed",
                category.type,
                category.display_name,
                category.id,
            )
            # NOTE: 代码异常, 可以返回加载失败
            raise error_codes.CATEGORY_PLUGIN_LOAD_FAIL

        try:
            login_class().check(profile, password)
        except Exception:
            create_profile_log(
                profile=profile,
                operation="LogIn",
                request=request,
                params={"is_success": False, "reason": LogInFailReason.BAD_PASSWORD.value},
            )
            logger.exception("login check, check profile<%s> of %s failed", profile.username, message_detail)
            # NOTE: 这里不能使用其他错误, 一律是 PASSWORD_ERROR, 安全问题
            raise error_codes.PASSWORD_ERROR

        self._check_password_status(request, profile, config_loader, time_aware_now)
        self._check_account_status(request, profile)

        create_profile_log(profile=profile, operation="LogIn", request=request, params={"is_success": True})
        return Response(data=ProfileSerializer(profile, context={"request": request}).data)

    def _check_password_status(
        self, request, profile: Profile, config_loader: ConfigProvider, time_aware_now: datetime.datetime
    ):
        """当密码校验成功后，检查用户密码状态"""
        # 密码状态校验:初始密码未修改
        # 暂时跳过判断 admin，考虑在 login 模块未升级替换时，admin 可以在 SaaS 配置中关掉该特性
        if (
            not profile.is_superuser
            and config_loader.get("force_reset_first_login")
            and profile.password_update_time is None
        ):
            create_profile_log(
                profile=profile,
                operation="LogIn",
                request=request,
                params={"is_success": False, "reason": LogInFailReason.SHOULD_CHANGE_INITIAL_PASSWORD.value},
            )

            raise error_codes.SHOULD_CHANGE_INITIAL_PASSWORD.format(
                data=self._generate_reset_passwd_url_with_token(profile)
            )

        # 密码状态校验:密码过期
        valid_period = datetime.timedelta(days=profile.password_valid_days)
        if (
            profile.password_valid_days > 0
            and ((profile.password_update_time or profile.latest_password_update_time) + valid_period) < time_aware_now
        ):
            create_profile_log(
                profile=profile,
                operation="LogIn",
                request=request,
                params={"is_success": False, "reason": LogInFailReason.EXPIRED_PASSWORD.value},
            )

            raise error_codes.PASSWORD_EXPIRED.format(data=self._generate_reset_passwd_url_with_token(profile))

    def _check_account_status(self, request, profile: Profile):
        """
        校验登录账号状态
        """
        expired_at = profile.account_expiration_date - datetime.date.today()
        if expired_at.days < 0:
            create_profile_log(
                profile=profile,
                operation="LogIn",
                request=request,
                params={"is_success": False, "reason": LogInFailReason.EXPIRED_USER.value},
            )
            raise error_codes.USER_IS_EXPIRED

    # pylint: disable=function-name-too-long
    @staticmethod
    def _generate_reset_passwd_url_with_token(profile: Profile) -> dict:
        data = {}
        try:
            token_holder = ProfileTokenHolder.objects.create(
                profile=profile, token_expire_seconds=settings.PAGE_TOKEN_EXPIRE_SECONDS
            )
        except Exception:  # pylint: disable=broad-except
            logger.exception("failed to create token for password reset. [profile.username=%s]", profile.username)
        else:
            data.update({"reset_password_url": make_passwd_reset_url_by_token(token_holder.token)})

        return data

    @method_decorator(clear_cache_if_succeed)
    @swagger_auto_schema(request_body=LoginUpsertSerializer)
    def upsert(self, request):
        # 理论上登录不应该开另外的写入接口（因为行为预期不确定）
        serializer = LoginUpsertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        if validated_data.get("position"):
            logger.info("position 字段<%s>暂不同步", validated_data.pop("position"))

        username = serializer.validated_data.pop("username")
        domain = serializer.validated_data.pop("domain", None)

        iso_code = None
        if "iso_code" in validated_data:
            iso_code = validated_data.pop("iso_code")

        try:
            category = ProfileCategory.objects.get(domain=domain)
            # 当 domain 存在时，校验 username
            validate_username(username)
        except ProfileCategory.DoesNotExist:
            if not domain:
                try:
                    # username may contain domain
                    username, domain = parse_username_domain(username)
                    category = ProfileCategory.objects.get(domain=domain)
                except Exception:  # pylint: disable=broad-except
                    category = ProfileCategory.objects.get_default()
            else:
                raise error_codes.DOMAIN_UNKNOWN

        profile, created = Profile.objects.update_or_create(
            username=username,
            domain=category.domain,
            category_id=category.id,
            defaults=validated_data,
        )
        if created:
            logger.info("user<%s/%s> created by login", category.id, username)

        if iso_code:
            try:
                # NOTE: 这里直接用iso_code设置country_code, 无视原来的country_code
                # 原因: 目前产品只暴露iso_code, country_code是内部的
                profile.country_code, profile.iso_code = align_country_iso_code(
                    country_code="",
                    iso_code=iso_code,
                )
            except ValueError:
                profile.country_code = settings.DEFAULT_COUNTRY_CODE
                profile.iso_code = settings.DEFAULT_IOS_CODE

            try:
                profile.save()
            except Exception:  # pylint: disable=broad-except
                logger.exception("failed to update iso_code for profile %s", username)
                # do nothing

        return Response(data=ProfileSerializer(profile, context={"request": request}).data)

    @method_decorator(cache_page(settings.GLOBAL_CACHES_TIMEOUT))
    @swagger_auto_schema(request_body=LoginBatchQuerySerializer)
    def batch_query(self, request):
        serializer = LoginBatchQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not serializer.is_valid():
            raise error_codes.ERROR_FORMAT

        username_list = serializer.validated_data.get("username_list", None)
        domain_username_map = defaultdict(list)

        for x in username_list:
            username, domain = parse_username_domain(x)
            if not domain:
                # default domain
                domain = ProfileCategory.objects.get_default().domain

            domain_username_map[domain].append(username)

        # logger.debug("going to query username list: %s", username_list)
        if not domain_username_map:
            profiles = Profile.objects.filter(enabled=True)
        else:
            target_lookups = []
            for domain in domain_username_map:
                target_lookups.append(Q(domain=domain, username__in=domain_username_map[domain]))

            profiles = Profile.objects.filter(enabled=True).filter(functools.reduce(or_, target_lookups))

        # 由于当前只继承了 viewSet，需要需要额外添加 context
        return Response(data=LoginBatchResponseSerializer(profiles, many=True, context={"request": request}).data)
