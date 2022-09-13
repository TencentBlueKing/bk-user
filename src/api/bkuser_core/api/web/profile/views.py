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

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from rest_framework import generics
from rest_framework.response import Response

from .serializers import (
    LoginProfileRetrieveSerializer,
    LoginProfileSerializer,
    ProfileSearchResultSerializer,
    ProfileSearchSerializer,
    ProfileUpdateSerializer,
)
from bkuser_core.api.web.utils import get_category, get_username
from bkuser_core.api.web.viewset import CustomPagination
from bkuser_core.audit.constants import OperationType
from bkuser_core.audit.utils import create_general_log
from bkuser_core.bkiam.permissions import IAMAction, ManageDepartmentProfilePermission, Permission
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.error_codes import error_codes
from bkuser_core.profiles.models import Profile
from bkuser_core.profiles.password import PasswordValidator
from bkuser_core.profiles.signals import post_profile_update
from bkuser_core.profiles.utils import align_country_iso_code, check_former_passwords, parse_username_domain
from bkuser_core.user_settings.exceptions import SettingHasBeenDisabledError
from bkuser_core.user_settings.loader import ConfigProvider

logger = logging.getLogger(__name__)


class LoginProfileRetrieveApi(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        slz = LoginProfileRetrieveSerializer(data=request.query_params)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data
        username = data["username"]

        username, domain = parse_username_domain(username)
        if not domain:
            domain = ProfileCategory.objects.get(default=True).domain

        profile = Profile.objects.get(username=username, domain=domain)

        return Response(LoginProfileSerializer(profile).data)


class ProfileSearchApi(generics.ListAPIView):
    serializer_class = ProfileSearchResultSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        serializer = ProfileSearchSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        category_id = data.get("category_id")

        username = get_username(self.request)
        category = get_category(category_id)
        Permission().allow_category_action(username, IAMAction.VIEW_CATEGORY, category)

        queryset = Profile.objects.filter(category_id=category_id, enabled=True)

        if data.get("username"):
            queryset = queryset.filter(username__icontains=data["username"])
        if data.get("display_name"):
            queryset = queryset.filter(display_name__icontains=data["display_name"])
        if data.get("email"):
            queryset = queryset.filter(email__icontains=data["email"])
        if data.get("telephone"):
            queryset = queryset.filter(telephone__icontains=data["telephone"])

        if data.get("status"):
            queryset = queryset.filter(status=data["status"])
        if data.get("staff_status"):
            queryset = queryset.filter(staff_status=data["staff_status"])

        if data.get("departments"):
            queryset = queryset.filter(departments__in=data["departments"])

        # NOTE: 这里相对原来/api/v3/profiles/?category_id 的差异是 enabled=True
        return queryset


class ProfileRetrieveUpdateDeleteApi(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [ManageDepartmentProfilePermission]
    queryset = Profile.objects.all()
    lookup_url_kwarg = "id"
    serializer_class = ProfileSearchResultSerializer

    def _update(self, request, partial):
        instance = self.get_object()
        serializer = ProfileUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        operate_type = OperationType.UPDATE.value

        validated_data = serializer.validated_data

        # 只允许本地目录修改
        if not ProfileCategory.objects.check_writable(instance.category_id):
            raise error_codes.CANNOT_MANUAL_WRITE_INTO

        # 普通字段
        for key, value in validated_data.items():
            setattr(instance, key, value)

        # FIXME: 可以简化, 不要搞那么复杂
        # 提前将多对多字段拿出
        # Django 2.2 以后不能直接设置
        # https://stackoverflow.com/questions/50015204/direct-assignment-to-the-forward-side-of-a-many-to-many-set-is-prohibited-use-e
        m2m_keys = ["departments", "leader"]
        m2m_fields = {}
        for k in m2m_keys:
            try:
                m2m_fields[k] = validated_data.pop(k)
            except KeyError:
                pass
        # 多对多字段
        for key, value in m2m_fields.items():
            getattr(instance, key).set(value)

        update_summary = {"request": request}
        # 密码修改加密
        if validated_data.get("password"):
            operate_type = (
                OperationType.FORGET_PASSWORD.value
                if request.headers.get("User-From-Token")
                else OperationType.ADMIN_RESET_PASSWORD.value
            )

            pending_password = validated_data.get("password")
            config_loader = ConfigProvider(category_id=instance.category_id)
            try:
                max_password_history = config_loader.get("max_password_history", settings.DEFAULT_MAX_PASSWORD_HISTORY)
                if check_former_passwords(instance, pending_password, int(max_password_history)):
                    raise error_codes.PASSWORD_DUPLICATED.f(max_password_history=max_password_history)
            except SettingHasBeenDisabledError:
                logger.info("category<%s> has disabled checking password", instance.category_id)

            PasswordValidator(
                min_length=int(config_loader["password_min_length"]),
                max_length=settings.PASSWORD_MAX_LENGTH,
                include_elements=config_loader["password_must_includes"],
                exclude_elements_config=config_loader["exclude_elements_config"],
            ).validate(pending_password)

            instance.password = make_password(pending_password)
            instance.password_update_time = now()
            update_summary.update({"should_notify": True, "raw_password": pending_password})

        # 对齐 country code
        try:
            instance.country_code, instance.iso_code = align_country_iso_code(
                country_code=validated_data.get("country_code", ""),
                iso_code=validated_data.get("iso_code", ""),
            )
        except ValueError:
            instance.country_code = settings.DEFAULT_COUNTRY_CODE
            instance.iso_code = settings.DEFAULT_IOS_CODE

        try:
            instance.save()
        except Exception:  # pylint: disable=broad-except
            logger.exception("failed to update profile")
            return error_codes.SAVE_USER_INFO_FAILED

        post_profile_update.send(
            sender=self,
            instance=instance,
            operator=request.operator,
            extra_values=update_summary,
        )

        create_general_log(
            operator=request.operator,
            operate_type=operate_type,
            operator_obj=instance,
            request=request,
        )
        return Response(self.serializer_class(instance).data)

    def update(self, request, *args, **kwargs):
        """更新用户"""
        return self._update(request, partial=False)

    def partial_update(self, request, *args, **kwargs):
        """更新用户部分字段"""
        return self._update(request, partial=True)


class ProfileOperationRestorationApi(generics.CreateAPIView):
    permission_classes = [ManageDepartmentProfilePermission]
    queryset = Profile.objects.all()
    lookup_url_kwarg = "id"

    def post(self, request, *args, **kwargs):
        """软删除恢复"""
        # FIXME: maybe should change to a custom mixin
        instance = self.get_object()

        # 相对原先的区别: 不需要检查是否已开启
        # if instance.enabled:
        #     raise error_codes.RESOURCE_ALREADY_ENABLED

        try:
            instance.enable()
        except Exception:
            logger.exception("failed to restoration instance: %s", instance)
            raise error_codes.RESOURCE_RESTORATION_FAILED
        return Response()
