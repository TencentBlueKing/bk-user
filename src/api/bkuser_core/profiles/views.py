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

from bkuser_core.audit.constants import LogInFailReasonEnum, OperationEnum
from bkuser_core.audit.utils import create_general_log, create_profile_log
from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.loader import get_plugin_by_category
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.cache import clear_cache_if_succeed
from bkuser_core.common.constants import LOOKUP_FIELD_NAME, LOOKUP_PARAM
from bkuser_core.common.error_codes import error_codes
from bkuser_core.common.serializers import (
    AdvancedListSerializer,
    AdvancedRetrieveSerialzier,
    BatchRetrieveSerializer,
    EmptySerializer,
)
from bkuser_core.common.viewset import AdvancedBatchOperateViewSet, AdvancedListAPIView, AdvancedModelViewSet
from bkuser_core.departments import serializers as department_serializer
from bkuser_core.user_settings.loader import ConfigProvider
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.exceptions import FieldError, MultipleObjectsReturned
from django.db.models import F, Q
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework_jsonp.renderers import JSONPRenderer

from bkuser_global.utils import force_str_2_bool

from . import serializers as local_serializers
from .constants import ProfileStatus
from .exceptions import CountryISOCodeNotMatch, ProfileEmailEmpty
from .filters import ProfileSearchFilter
from .models import DynamicFieldInfo, LeaderThroughModel, Profile, ProfileTokenHolder
from .password import PasswordValidator
from .signals import post_profile_create, post_profile_update
from .tasks import send_password_by_email
from .utils import (
    align_country_iso_code,
    check_former_passwords,
    force_use_raw_username,
    make_password_by_config,
    parse_username_domain,
)
from .validators import validate_username

logger = logging.getLogger(__name__)


class ProfileViewSet(AdvancedModelViewSet, AdvancedListAPIView):
    queryset = Profile.objects.filter()
    serializer_class = local_serializers.ProfileSerializer
    lookup_field = "username"
    filter_backends = [ProfileSearchFilter, filters.OrderingFilter]

    relation_fields = ["departments", "leader"]

    def get_object(self):
        _default_lookup_field = self.lookup_field

        self.lookup_url_kwarg = LOOKUP_FIELD_NAME

        try:
            request_lookup_field = self.request.query_params[LOOKUP_PARAM]
            self.lookup_field = request_lookup_field
        except KeyError:
            """使用默认查询字段"""

        if not self.lookup_field == "username":
            try:
                return super(AdvancedModelViewSet, self).get_object()
            except FieldError:
                self.lookup_field = _default_lookup_field
                return super(AdvancedModelViewSet, self).get_object()

        # username 曾作为键，需要为旧系统兼容
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        username, domain = parse_username_domain(username_with_domain=self.kwargs[lookup_url_kwarg])
        if not domain:
            domain = ProfileCategory.objects.get(default=True).domain

        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {"username": username, "domain": domain}
        obj = get_object_or_404(queryset, **filter_kwargs)

        return obj

    def get_serializer_class(self):
        """Serializer 路由"""
        if self.action in ("create", "update", "partial_update"):
            return local_serializers.CreateProfileSerializer
        elif self.action in ("list",):
            return local_serializers.RapidProfileSerializer
        else:
            return self.serializer_class

    def get_serializer_context(self):
        origin = super().get_serializer_context()
        origin.update({"extra_defaults": DynamicFieldInfo.objects.get_extras_default_values()})
        return origin

    def get_renderers(self):
        # 只限定特定的 API
        if self.action not in ("list",):
            return super().get_renderers()

        if force_str_2_bool(self.request.META.get(settings.FORCE_JSONP_HEADER, False)):
            return [JSONPRenderer()]
        else:
            return super().get_renderers()

    @swagger_auto_schema(
        query_serializer=local_serializers.ProfileDepartmentSerializer(),
        responses={"200": department_serializer.SimpleDepartmentSerializer(many=True)},
    )
    def get_departments(self, request, lookup_value):
        """获取用户所属部门信息"""
        instance = self.get_object()

        # 当前的 with_family 为兼容参数名, TODO: 协同 PaaS 修改为 with_ancestor
        with_family = request.query_params.get("with_family", False)
        with_ancestor = request.query_params.get("with_ancestors", False)

        departments = instance.departments.all().order_by("-level", "lft")

        serializer = department_serializer.SimpleDepartmentSerializer
        if with_family or with_ancestor:
            serializer = department_serializer.DepartmentsWithFamilySerializer

        return Response(data=serializer(departments, many=True).data)

    @swagger_auto_schema(
        query_serializer=AdvancedRetrieveSerialzier(),
        responses={"200": department_serializer.SimpleDepartmentSerializer(many=True)},
    )
    def get_leaders(self, request, lookup_value):
        """获取用户上级信息 包含该用户关联的所有上级信息"""
        instance = self.get_object()
        leaders = instance.leader.all().order_by("id")

        return Response(data=self.serializer_class(leaders, many=True).data)

    @method_decorator(cache_page(settings.GLOBAL_CACHES_TIMEOUT))
    @swagger_auto_schema(query_serializer=AdvancedListSerializer())
    def list(self, request, *args, **kwargs):
        """获取用户列表"""
        self.check_permissions(request)
        _query_slz = AdvancedListSerializer(data=request.query_params)
        _query_slz.is_valid(True)
        query_data = _query_slz.validated_data

        fields = query_data.get("fields", self.get_serializer().fields)
        self._ensure_enabled_field(request, fields=fields)
        self._check_fields(fields)

        try:
            queryset = self.filter_queryset(self.get_queryset())
        except Exception:
            logger.exception("failed to query profiles")
            raise error_codes.QUERY_PARAMS_ERROR

        # 提前将关系表拿出来
        chosen_fields = [_f for _f in self.relation_fields if _f in fields]
        if chosen_fields:
            queryset = queryset.prefetch_related(*chosen_fields)

        # 当用户请求数据时，判断其是否强制输出原始 username
        if not force_use_raw_username(request):
            # 直接在 DB 中拼接 username & domain，比在 serializer 中快很多
            if "username" in fields:
                default_domain = ProfileCategory.objects.get_default().domain
                queryset = queryset.extra(
                    select={"username": "if(`domain`= %s, username, CONCAT(username, '@', domain))"},
                    select_params=(default_domain,),
                )

        page = self.paginate_queryset(queryset)
        # page may be empty list
        if page is not None:
            serializer = self.get_serializer(page, fields=fields, many=True)
            return self.get_paginated_response(serializer.data)

        # 全量数据太大，使用 serializer 效率非常低
        # 由于存在多对多字段，所以返回列表会平铺展示，同一个 username 会多次展示
        # https://docs.djangoproject.com/en/1.11/ref/models/querysets/#values
        return Response(data=list(queryset.values(*fields)))

    @method_decorator(clear_cache_if_succeed)
    @swagger_auto_schema(
        request_body=local_serializers.CreateProfileSerializer,
        responses={"200": local_serializers.ProfileSerializer()},
    )
    def create(self, request, *args, **kwargs):
        """创建用户"""
        serializer = local_serializers.CreateProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        from bkuser_core.departments.models import Department

        deps = Department.objects.filter(id__in=validated_data.get("departments", []))
        for dep in deps:
            self.check_object_permissions(request, obj=dep)

        if not validated_data.get("category_id", None):
            default_category = ProfileCategory.objects.get_default()
            serializer.validated_data["category_id"] = default_category.id
            serializer.validated_data["domain"] = default_category.domain
        else:
            # 只允许本地目录修改
            if not ProfileCategory.objects.check_writable(validated_data["category_id"]):
                raise error_codes.CANNOT_MANUAL_WRITE_INTO

            serializer.validated_data["domain"] = ProfileCategory.objects.get(pk=validated_data["category_id"]).domain
        # `ConfigProvider._refresh_config` 过滤 enabled=True
        if not ProfileCategory.objects.get(pk=validated_data["category_id"]).enabled:
            raise error_codes.CATEGORY_NOT_ENABLED

        try:
            existed = Profile.objects.get(
                username=serializer.validated_data["username"],
                category_id=serializer.validated_data["category_id"],
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
            serializer.validated_data["category_id"], return_raw=True
        )
        serializer.validated_data["password"] = make_password(raw_password)
        create_summary.update({"should_notify": should_notify, "raw_password": raw_password})

        # 对齐 country code
        try:
            (
                serializer.validated_data["country_code"],
                serializer.validated_data["iso_code"],
            ) = align_country_iso_code(
                country_code=validated_data.get("country_code", ""),
                iso_code=validated_data.get("iso_code", ""),
            )
        except (ValueError, CountryISOCodeNotMatch):
            serializer.validated_data["country_code"] = settings.DEFAULT_COUNTRY_CODE
            serializer.validated_data["iso_code"] = settings.DEFAULT_IOS_CODE

        try:
            instance = serializer.save()
        except Exception:
            logger.exception("failed to save profile")
            raise error_codes.SAVE_USER_INFO_FAILED

        # 善后工作
        post_profile_create.send(
            sender=self,
            profile=instance,
            operator=request.operator,
            extra_values=create_summary,
            operation_type=OperationEnum.CREATE.value,
        )
        return Response(self.serializer_class(instance).data, status=status.HTTP_201_CREATED)

    @method_decorator(clear_cache_if_succeed)
    def _update(self, request, partial):
        instance = self.get_object()
        serializer = local_serializers.UpdateProfileSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # 只允许本地目录修改
        if not ProfileCategory.objects.check_writable(instance.category_id):
            raise error_codes.CANNOT_MANUAL_WRITE_INTO

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

        # 普通字段
        for key, value in validated_data.items():
            setattr(instance, key, value)
        # 多对多字段
        for key, value in m2m_fields.items():
            getattr(instance, key).set(value)

        update_summary = {"request": request}
        # 密码修改加密
        if validated_data.get("password"):
            pending_password = validated_data.get("password")
            if check_former_passwords(instance, pending_password):
                raise error_codes.PASSWORD_DUPLICATED

            config_loader = ConfigProvider(category_id=instance.category_id)
            PasswordValidator(
                min_length=int(config_loader["password_min_length"]),
                max_length=settings.PASSWORD_MAX_LENGTH,
                required_element_names=config_loader["password_must_includes"],
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
            profile=instance,
            operator=request.operator,
            extra_values=update_summary,
            operation_type=OperationEnum.UPDATE.value,
        )
        return Response(self.serializer_class(instance).data)

    @swagger_auto_schema(
        query_serializer=AdvancedRetrieveSerialzier(),
        request_body=local_serializers.UpdateProfileSerializer,
        responses={"200": local_serializers.ProfileSerializer()},
    )
    def update(self, request, *args, **kwargs):
        """更新用户"""
        return self._update(request, partial=False)

    @swagger_auto_schema(
        query_serializer=AdvancedRetrieveSerialzier(),
        request_body=local_serializers.UpdateProfileSerializer,
        responses={"200": local_serializers.ProfileSerializer()},
    )
    def partial_update(self, request, *args, **kwargs):
        """更新用户部分字段"""
        return self._update(request, partial=True)

    @swagger_auto_schema(query_serializer=AdvancedRetrieveSerialzier())
    def destroy(self, request, *args, **kwargs):
        """删除用户
        目前采用软删除
        """
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        query_serializer=AdvancedRetrieveSerialzier(),
        request_body=local_serializers.ProfileModifyPasswordSerializer,
        responses={"200": EmptySerializer()},
    )
    def modify_password(self, request, *args, **kwargs):
        """修改用户密码
        不同于直接更新 password 字段，修改密码 API 面向普通用户，需要校验原密码
        """
        instance = self.get_object()
        serializer = local_serializers.ProfileModifyPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]
        if check_former_passwords(instance, new_password):
            raise error_codes.PASSWORD_DUPLICATED

        if not instance.check_password(old_password):
            raise error_codes.PASSWORD_ERROR

        config_loader = ConfigProvider(category_id=instance.category_id)
        PasswordValidator(
            min_length=int(config_loader["password_min_length"]),
            max_length=settings.PASSWORD_MAX_LENGTH,
            required_element_names=config_loader["password_must_includes"],
        ).validate(new_password)

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
            profile=instance,
            operator=request.operator,
            extra_values=modify_summary,
            operation_type=OperationEnum.UPDATE.value,
        )
        return Response(data=local_serializers.ProfileMinimalSerializer(instance).data)

    @swagger_auto_schema(
        query_serializer=AdvancedRetrieveSerialzier(),
        request_body=EmptySerializer,
        responses={"200": local_serializers.ProfileTokenSerializer()},
    )
    def generate_token(self, request, *args, **kwargs):
        """生成用户 Token
        生成代表用户的 Token
        """
        instance = self.get_object()
        token_holder = ProfileTokenHolder.objects.create(profile=instance)

        try:
            send_password_by_email.delay(profile_id=instance.id, token=token_holder.token, init=False)
        except ProfileEmailEmpty:
            raise error_codes.EMAIL_NOT_PROVIDED
        except Exception:  # pylint: disable=broad-except
            logger.exception("failed to send password via email")

        return Response(data=local_serializers.ProfileTokenSerializer(token_holder).data)

    @swagger_auto_schema(
        manual_parameters=[],
        responses={"200": local_serializers.ProfileSerializer()},
        tags=["profiles"],
    )
    def retrieve_by_token(self, request, token, *args, **kwargs):
        """通过 Token 获取用户
        通过有效的 token 获取用户信息
        """
        try:
            token_holder = ProfileTokenHolder.objects.get(token=token, enabled=True)
        except ProfileTokenHolder.DoesNotExist:
            logger.info("token<%s> not exist in db", token)
            raise error_codes.CANNOT_GET_TOKEN_HOLDER

        if token_holder.expired:
            raise error_codes.PROFILE_TOKEN_EXPIRED

        return Response(data=local_serializers.ProfileSerializer(token_holder.profile).data)


class BatchProfileViewSet(AdvancedBatchOperateViewSet):
    serializer_class = local_serializers.ProfileSerializer
    queryset = Profile.objects.filter(enabled=True)

    def get_serializer_class(self):
        """Serializer 路由"""
        if self.action in ("multiple_update", "multiple_delete"):
            return local_serializers.UpdateProfileSerializer
        else:
            return self.serializer_class

    @swagger_auto_schema(
        query_serializer=BatchRetrieveSerializer(), responses={"200": local_serializers.ProfileSerializer(many=True)}
    )
    def multiple_retrieve(self, request):
        """批量获取用户"""
        return super().multiple_retrieve(request)

    @swagger_auto_schema(
        request_body=local_serializers.UpdateProfileSerializer(many=True),
        responses={"200": local_serializers.ProfileSerializer(many=True)},
    )
    def multiple_update(self, request):
        """批量更新用户"""
        return super().multiple_update(request)

    @swagger_auto_schema(
        request_body=local_serializers.UpdateProfileSerializer(many=True),
        responses={"200": EmptySerializer()},
    )
    def multiple_delete(self, request):
        """批量删除用户"""
        return super().multiple_delete(request)


class ProfileLoginViewSet(viewsets.ViewSet):
    """登陆均为兼容代码"""

    @swagger_auto_schema(
        request_body=local_serializers.ProfileLoginSerializer,
        responses={"200": local_serializers.ProfileSerializer()},
    )
    def login(self, request):
        """登录信息校验"""
        serializer = local_serializers.ProfileLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")
        domain = serializer.validated_data.get("domain", None)

        # 无指定 domain 时, 选择默认域
        if not domain:
            category = ProfileCategory.objects.get_default()
        else:
            try:
                category = ProfileCategory.objects.get(domain=domain)
            except ProfileCategory.DoesNotExist:
                raise error_codes.DOMAIN_UNKNOWN

            if category.inactive:
                raise error_codes.CATEGORY_NOT_ENABLED

        # 这里不检查具体的用户名格式，只判断是否能够获取到对应用户
        try:
            profile = Profile.objects.get(
                Q(email=username) | Q(telephone=username) | Q(username=username),
                domain=category.domain,
            )
        except Profile.DoesNotExist:
            raise error_codes.PASSWORD_ERROR
        except MultipleObjectsReturned:
            raise error_codes.PASSWORD_ERROR

        # Admin 用户只需直接判断 密码是否正确 (只有本地目录有密码配置)
        if not profile.is_superuser and category.type in [CategoryType.LOCAL.value]:

            # 判断账户状态
            if profile.status in [
                ProfileStatus.DISABLED.value,
                ProfileStatus.DELETED.value,
            ]:
                create_profile_log(
                    profile=profile,
                    operation="LogIn",
                    request=request,
                    params={"is_success": False, "reason": LogInFailReasonEnum.DISABLED_USER.value},
                )
                raise error_codes.USER_IS_DISABLED
            elif profile.status == ProfileStatus.LOCKED.value:
                create_profile_log(
                    profile=profile,
                    operation="LogIn",
                    request=request,
                    params={"is_success": False, "reason": LogInFailReasonEnum.LOCKED_USER.value},
                )
                raise error_codes.USER_IS_LOCKED

            # 获取密码配置
            config_loader = ConfigProvider(category_id=category.id)
            auto_unlock_seconds = int(config_loader["auto_unlock_seconds"])
            max_trail_times = int(config_loader["max_trail_times"])

            # 密码状态校验:密码过期
            time_aware_now = now()
            valid_period = datetime.timedelta(days=profile.password_valid_days)
            if (
                profile.password_valid_days > 0
                and ((profile.password_update_time or profile.latest_password_update_time) + valid_period)
                < time_aware_now
            ):
                create_profile_log(
                    profile=profile,
                    operation="LogIn",
                    request=request,
                    params={"is_success": False, "reason": LogInFailReasonEnum.EXPIRED_PASSWORD.value},
                )
                raise error_codes.PASSWORD_EXPIRED

            # 错误登录次数校验
            if profile.bad_check_cnt >= max_trail_times > 0:
                from_last_check_seconds = (time_aware_now - profile.latest_check_time).total_seconds()
                retry_after_wait = int(auto_unlock_seconds - from_last_check_seconds)

                if retry_after_wait > 0:
                    create_profile_log(
                        profile=profile,
                        operation="LogIn",
                        request=request,
                        params={"is_success": False, "reason": LogInFailReasonEnum.TOO_MANY_FAILURE.value},
                    )
                    raise error_codes.TOO_MANY_TRY.f(f"请 {retry_after_wait}s 后再试")

        try:
            login_class = get_plugin_by_category(category).login_handler_cls
        except Exception:
            logger.exception(
                "category<%s-%s-%s> load login handler failed",
                category.type,
                category.display_name,
                category.id,
            )
            raise error_codes.LOAD_LOGIN_HANDLER_FAILED

        try:
            login_class().check(profile, password)
            create_profile_log(
                profile=profile,
                operation="LogIn",
                request=request,
                params={"is_success": True},
            )
        except Exception:
            create_profile_log(
                profile=profile,
                operation="LogIn",
                request=request,
                params={"is_success": False, "reason": LogInFailReasonEnum.BAD_PASSWORD.value},
            )
            logger.exception("check profile<%s> failed", profile.username)
            raise error_codes.PASSWORD_ERROR

        return Response(data=local_serializers.ProfileSerializer(profile, context={"request": request}).data)

    @method_decorator(clear_cache_if_succeed)
    @swagger_auto_schema(request_body=local_serializers.LoginUpsertSerializer)
    def upsert(self, request):
        # 理论上登录不应该开另外的写入接口（因为行为预期不确定）
        serializer = local_serializers.LoginUpsertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        if validated_data.get("position"):
            logger.info("position 字段<%s>暂不同步", validated_data.pop("position"))

        username = serializer.validated_data.pop("username")
        domain = serializer.validated_data.pop("domain", None)

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

        return Response(data=local_serializers.ProfileSerializer(profile, context={"request": request}).data)

    @method_decorator(cache_page(settings.GLOBAL_CACHES_TIMEOUT))
    @swagger_auto_schema(request_body=local_serializers.LoginBatchQuerySerializer)
    def batch_query(self, request):
        serializer = local_serializers.LoginBatchQuerySerializer(data=request.data)
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

        logger.info("going to query username list: %s", username_list)
        if not domain_username_map:
            profiles = Profile.objects.filter(enabled=True)
        else:
            target_lookups = []
            for domain in domain_username_map:
                target_lookups.append(Q(domain=domain, username__in=domain_username_map[domain]))

            profiles = Profile.objects.filter(enabled=True).filter(functools.reduce(or_, target_lookups))

        # 由于当前只继承了 viewSet，需要需要额外添加 context
        return Response(
            data=local_serializers.LoginBatchResponseSerializer(profiles, many=True, context={"request": request}).data
        )


class DynamicFieldsViewSet(AdvancedModelViewSet, AdvancedListAPIView):
    queryset = DynamicFieldInfo.objects.filter(enabled=True)
    serializer_class = local_serializers.DynamicFieldsSerializer
    lookup_field: str = "name"
    cache_name = "profiles"

    def get_serializer(self, *args, **kwargs):
        if self.action in ["create"]:
            return local_serializers.CreateFieldsSerializer(*args, **kwargs)
        else:
            return self.serializer_class(*args, **kwargs)

    @method_decorator(clear_cache_if_succeed)
    @swagger_auto_schema(
        request_body=local_serializers.CreateFieldsSerializer,
        responses={"200": local_serializers.DynamicFieldsSerializer()},
    )
    def create(self, request, *args, **kwargs):
        """创建自定义字段"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # 默认加到最后
        order = validated_data.get("order", 0)
        if not order:
            validated_data["order"] = DynamicFieldInfo.objects.get_max_order() + 1

        instance = serializer.save()
        headers = self.get_success_headers(serializer.data)

        # 审计记录
        create_general_log(
            operator=request.operator,
            operate_type=OperationEnum.CREATE.value,
            operator_obj=instance,
            request=request,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @method_decorator(clear_cache_if_succeed)
    def _update(self, request, partial):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # 内置字段 只能更新 order & visible
        if not instance.configurable and set(validated_data.keys()) - {
            "order",
            "visible",
        }:
            raise error_codes.FIELD_IS_NOT_EDITABLE.f("该字段无法更新")

        if "name" in validated_data:
            raise error_codes.FIELD_IS_NOT_EDITABLE.f("字段 key 值无法更新")

        updating_order = validated_data.get("order", False)
        if updating_order:
            """整理 order"""
            DynamicFieldInfo.objects.update_order(instance, updating_order)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        # 审计记录
        create_general_log(
            operator=request.operator,
            operate_type=OperationEnum.UPDATE.value,
            operator_obj=instance,
            request=request,
        )
        return Response(self.serializer_class(instance).data)

    @swagger_auto_schema(query_serializer=AdvancedRetrieveSerialzier())
    def update(self, request, *args, **kwargs):
        """更新自定义字段"""
        return self._update(request, partial=False)

    @swagger_auto_schema(query_serializer=AdvancedRetrieveSerialzier())
    def partial_update(self, request, *args, **kwargs):
        """部分更新自定义字段"""
        return self._update(request, partial=True)

    @swagger_auto_schema(query_serializer=AdvancedRetrieveSerialzier())
    def destroy(self, request, *args, **kwargs):
        """移除自定义字段"""
        instance = self.get_object()
        # 内置字段不允许删除
        if instance.builtin:
            raise error_codes.BUILTIN_FIELD_CANNOT_BE_DELETED

        # 保证 order 密集
        DynamicFieldInfo.objects.filter(order__gt=instance.order).update(order=F("order") - 1)

        return super().destroy(request, *args, **kwargs)


class LeaderEdgeViewSet(AdvancedModelViewSet, AdvancedListAPIView):
    """上级边"""

    queryset = LeaderThroughModel.objects.filter(to_profile__enabled=True, from_profile__enabled=True)
    serializer_class = local_serializers.LeaderEdgeSerializer
    ordering = ["id"]
