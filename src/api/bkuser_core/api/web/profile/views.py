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
import logging

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import (
    LoginProfileOutputSLZ,
    LoginProfileRetrieveInputSLZ,
    ProfileBatchDeleteInputSLZ,
    ProfileBatchUpdateInputSLZ,
    ProfileCreateInputSLZ,
    ProfileSearchInputSLZ,
    ProfileSearchOutputSLZ,
    ProfileUpdateInputSLZ,
)
from bkuser_core.api.web.utils import get_category, get_operator, validate_password
from bkuser_core.api.web.viewset import CustomPagination
from bkuser_core.audit.constants import OperationType
from bkuser_core.audit.utils import audit_general_log, create_general_log
from bkuser_core.bkiam.permissions import IAMAction, ManageDepartmentProfilePermission, Permission
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.error_codes import error_codes
from bkuser_core.departments.models import Department
from bkuser_core.profiles.constants import ProfileStatus
from bkuser_core.profiles.exceptions import CountryISOCodeNotMatch
from bkuser_core.profiles.models import DynamicFieldInfo, Profile
from bkuser_core.profiles.signals import post_profile_create, post_profile_update
from bkuser_core.profiles.utils import (
    align_country_iso_code,
    check_old_password,
    make_password_by_config,
    parse_username_domain,
    should_check_old_password,
)
from bkuser_core.user_settings.constants import SettingsEnableNamespaces
from bkuser_core.user_settings.models import Setting, SettingMeta

logger = logging.getLogger(__name__)


class LoginProfileRetrieveApi(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        slz = LoginProfileRetrieveInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data
        username = data["username"]

        username, domain = parse_username_domain(username)
        if not domain:
            domain = ProfileCategory.objects.get(default=True).domain

        profile = Profile.objects.get(username=username, domain=domain)

        return Response(LoginProfileOutputSLZ(profile).data)


class ProfileSearchApi(generics.ListAPIView):
    serializer_class = ProfileSearchOutputSLZ
    pagination_class = CustomPagination

    def get_queryset(self):
        slz = ProfileSearchInputSLZ(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        category_id = data.get("category_id")

        if settings.ENABLE_IAM:
            operator = get_operator(self.request)
            category = get_category(category_id)
            Permission().allow_category_action(operator, IAMAction.VIEW_CATEGORY, category)

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
    serializer_class = ProfileSearchOutputSLZ

    def _update(self, request, partial):
        instance = self.get_object()
        slz = ProfileUpdateInputSLZ(instance, data=request.data, partial=partial)
        slz.is_valid(raise_exception=True)
        operate_type = OperationType.UPDATE.value
        validated_data = slz.validated_data

        # 前端是把extras字段打平提交的
        fields = DynamicFieldInfo.objects.filter(enabled=True).all()
        extra_fields = {key: value for key, value in request.data.items() if key not in validated_data}
        logger.info("%s %s", extra_fields.keys(), [x.name for x in fields if not x.builtin])
        unknown_fields = set(extra_fields.keys()) - set([x.name for x in fields if not x.builtin])  # noqa
        if unknown_fields:
            raise error_codes.UNKNOWN_FIELD.f(", ".join(list(unknown_fields)))

        extras = {key: value for key, value in extra_fields.items()}

        # 只允许本地目录修改
        if not ProfileCategory.objects.check_writable(instance.category_id):
            raise error_codes.CANNOT_MANUAL_WRITE_INTO

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

        # NOTE: do not change the order here
        # 普通字段
        for key, value in validated_data.items():
            setattr(instance, key, value)
        # 多对多字段
        for key, value in m2m_fields.items():
            getattr(instance, key).set(value)

        # extras 字段
        if extras:
            instance.extras.update(extras)

        update_summary = {"request": request}
        # 密码修改加密
        if validated_data.get("password"):
            # 如果重置的是admin账号的密码，需要对原始密码进行校验
            if should_check_old_password(username=instance.username):
                check_old_password(instance=instance, old_password=validated_data["old_password"], request=request)

            operate_type = (
                OperationType.FORGET_PASSWORD.value
                if request.headers.get("User-From-Token")
                else OperationType.ADMIN_RESET_PASSWORD.value
            )

            pending_password = validated_data.get("password")
            validate_password(instance, pending_password)

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

        # 过期状态，续期后需要调整为正常状态
        # Note: 前提是基于EXPIRED状态一定是从NORMAL状态变更来的
        if instance.status == ProfileStatus.EXPIRED.value and instance.account_expiration_date > now().date():
            instance.status = ProfileStatus.NORMAL.value

        try:
            instance.save()
        except Exception as e:  # pylint: disable=broad-except
            username = f"{instance.username}@{instance.domain}"
            logger.exception(f"failed to update profile<{username}>")
            raise error_codes.SAVE_USER_INFO_FAILED.f(exception_message=e)

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

    @audit_general_log(operate_type=OperationType.DELETE.value)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ProfileOperationRestorationApi(generics.CreateAPIView):
    permission_classes = [ManageDepartmentProfilePermission]
    queryset = Profile.objects.all()
    lookup_url_kwarg = "id"

    @audit_general_log(operate_type=OperationType.RESTORATION.value)
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


class ProfileCreateApi(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        """创建用户"""
        # FIXME: 重构, 简化(目前直接拷贝的原来代码)
        operator = get_operator(self.request)

        # do validate
        slz = ProfileCreateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        validated_data = slz.validated_data

        fields = DynamicFieldInfo.objects.filter(enabled=True).all()
        extra_fields = {key: value for key, value in request.data.items() if key not in validated_data}
        logger.info("%s %s", extra_fields.keys(), [x.name for x in fields if not x.builtin])
        unknown_fields = set(extra_fields.keys()) - set([x.name for x in fields if not x.builtin])  # noqa
        if unknown_fields:
            raise error_codes.UNKNOWN_FIELD.f(", ".join(list(unknown_fields)))

        slz.validated_data["extras"] = {key: value for key, value in extra_fields.items()}

        # NOTE: 其他字段, 自行放入extras

        # departments非空, 需要校验有对应department的管理权限; departments为空, 则绕过了第一次权限控制
        deps = Department.objects.filter(id__in=validated_data.get("departments", []))
        for dep in deps:
            Permission().allow_department_action(operator, IAMAction.MANAGE_DEPARTMENT, dep)

        category_id = validated_data.get("category_id", None)
        # category_id and domain
        if not category_id:
            default_category = ProfileCategory.objects.get_default()
            slz.validated_data["category_id"] = default_category.id
            slz.validated_data["domain"] = default_category.domain

            category_id = default_category.id
        else:
            # 只允许本地目录修改
            if not ProfileCategory.objects.check_writable(category_id):
                raise error_codes.CANNOT_MANUAL_WRITE_INTO

            slz.validated_data["domain"] = ProfileCategory.objects.get(pk=category_id).domain

        # account_expiration_date
        if not validated_data.get("account_expiration_date"):
            # FIXME: 提取常量
            # # 账户设置类型
            # ACCOUNT_NAMESPACE = "account"
            # # 账户有效期选项
            # ACCOUNT_EXPIRATION_DATE_KEY = "expired_after_days"
            # # 账户有效期为永久
            # ACCOUNT_EXPIRATION_TYPE_PERMANENT = -1
            meta = SettingMeta.objects.filter(
                key="expired_after_days", namespace=SettingsEnableNamespaces.ACCOUNT.value
            ).first()

            # NOTE: maybe None here if the meta is not set
            expired_after_days = -1
            expired_after_days_setting = Setting.objects.filter(category_id=category_id, meta=meta).first()
            if expired_after_days_setting:
                expired_after_days = expired_after_days_setting.value

            # 账户有效期，不传，默认设置为目录设置项
            if expired_after_days == -1:
                account_expiration_date = datetime.date(year=2100, month=1, day=1)
            else:
                account_expiration_date = now().date() + datetime.timedelta(days=expired_after_days)

            slz.validated_data["account_expiration_date"] = account_expiration_date

        # `ConfigProvider._refresh_config` 过滤 enabled=True
        if not ProfileCategory.objects.get(pk=category_id).enabled:
            raise error_codes.CATEGORY_NOT_ENABLED

        # 必须要有这个category的管理权限, 才能添加用户到这个目录下
        category = get_category(category_id)
        Permission().allow_category_action(operator, IAMAction.MANAGE_CATEGORY, category)

        try:
            existed = Profile.objects.get(
                username=slz.validated_data["username"],
                category_id=category_id,
            )
            if existed.enabled:
                raise error_codes.USER_ALREADY_EXISTED
            else:
                raise error_codes.USER_ALREADY_EXISTED.f(_("该用户处于被删除状态，请联系管理员恢复"))

        except Profile.DoesNotExist:
            pass

        # a summary of creating profile
        create_summary = {"request": request}
        # 生成密码
        raw_password, should_notify = make_password_by_config(
            category_id,
            return_raw=True,
        )
        slz.validated_data["password"] = make_password(raw_password)
        create_summary.update({"should_notify": should_notify, "raw_password": raw_password})

        # 对齐 country code
        try:
            (slz.validated_data["country_code"], slz.validated_data["iso_code"],) = align_country_iso_code(
                country_code=validated_data.get("country_code", ""),
                iso_code=validated_data.get("iso_code", ""),
            )
        except (ValueError, CountryISOCodeNotMatch):
            slz.validated_data["country_code"] = settings.DEFAULT_COUNTRY_CODE
            slz.validated_data["iso_code"] = settings.DEFAULT_IOS_CODE

        try:
            instance = slz.save()
        except Exception as e:
            username = f"{slz.validated_data['username']}@{slz.validated_data['domain']}"
            logger.exception(f"failed to create profile<{username}>")
            raise error_codes.SAVE_USER_INFO_FAILED.f(exception_message=e)

        # 善后工作
        post_profile_create.send(
            sender=self,
            instance=instance,
            operator=request.operator,
            extra_values=create_summary,
        )
        return Response(status=status.HTTP_201_CREATED)


class ProfileBatchApi(generics.RetrieveUpdateDestroyAPIView):
    # FIXME: 让前端把删除接口切换成删除单个用户, 而不是批量(低优先级)
    def delete(self, request, *args, **kwargs):
        """批量删除"""
        slz = ProfileBatchDeleteInputSLZ(data=request.data, many=True)
        slz.is_valid(raise_exception=True)

        operator = get_operator(request)
        data = slz.validated_data
        for obj in data:
            try:
                instance = Profile.objects.get(pk=obj["id"])
                create_general_log(
                    operator=operator,
                    operate_type=OperationType.DELETE.value,
                    operator_obj=instance,
                    request=request,
                )
            except ObjectDoesNotExist:
                logger.warning(
                    "obj <%s-%s> not found or already been deleted.",
                    self.queryset.model,
                    obj,
                )
                continue
            else:
                if settings.ENABLE_IAM:
                    # check permission
                    category = ProfileCategory.objects.get(pk=instance.category_id)
                    Permission().allow_category_action(operator, IAMAction.MANAGE_CATEGORY, category)

                # do
                instance.delete()

        return Response(status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """批量更新，必须传递 id 作为查找字段"""
        slz = ProfileBatchUpdateInputSLZ(data=request.data, many=True)
        slz.is_valid(raise_exception=True)

        operator = get_operator(request)
        data = slz.validated_data

        updating_instances = []
        for obj in data:
            try:
                instance = Profile.objects.get(pk=obj["id"])
            except ObjectDoesNotExist:
                logger.warning(
                    "obj <%s-%s> not found or already been deleted.",
                    self.queryset.model,
                    obj,
                )
                continue
            else:
                if settings.ENABLE_IAM:
                    # check permission
                    category = ProfileCategory.objects.get(pk=instance.category_id)
                    Permission().allow_category_action(operator, IAMAction.MANAGE_CATEGORY, category)

                create_general_log(
                    operator=operator,
                    operate_type=OperationType.UPDATE.value,
                    operator_obj=instance,
                    request=request,
                )

                # TODO: 限制非本地目录进行修改

                single_serializer = ProfileBatchUpdateInputSLZ(instance=instance, data=obj)
                single_serializer.is_valid(raise_exception=True)
                single_serializer.save()
                updating_instances.append(instance)

        return Response(status=status.HTTP_200_OK)
