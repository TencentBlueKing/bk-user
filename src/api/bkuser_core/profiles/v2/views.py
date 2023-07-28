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
from django.core.exceptions import FieldError
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework_jsonp.renderers import JSONPRenderer

from . import serializers as local_serializers
from bkuser_core.apis.v2.constants import LOOKUP_FIELD_NAME, LOOKUP_PARAM
from bkuser_core.apis.v2.serializers import AdvancedListSerializer, AdvancedRetrieveSerializer
from bkuser_core.apis.v2.viewset import AdvancedListAPIView, AdvancedModelViewSet
from bkuser_core.audit.constants import OperationType
from bkuser_core.audit.utils import create_general_log
from bkuser_core.categories.cache import get_default_category_domain_from_local_cache
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.cache import clear_cache_if_succeed
from bkuser_core.common.error_codes import error_codes
from bkuser_core.departments.v2 import serializers as department_serializer
from bkuser_core.profiles.exceptions import CountryISOCodeNotMatch
from bkuser_core.profiles.models import LeaderThroughModel, Profile
from bkuser_core.profiles.password import PasswordValidator
from bkuser_core.profiles.signals import post_profile_create, post_profile_update
from bkuser_core.profiles.utils import (
    align_country_iso_code,
    check_former_passwords,
    make_password_by_config,
    parse_username_domain,
    remove_sensitive_fields_for_profile,
)
from bkuser_core.profiles.v2.filters import ProfileSearchFilter
from bkuser_core.user_settings.exceptions import SettingHasBeenDisabledError
from bkuser_core.user_settings.loader import ConfigProvider
from bkuser_global.utils import force_str_2_bool

logger = logging.getLogger(__name__)


class ProfileViewSet(AdvancedModelViewSet, AdvancedListAPIView):
    queryset = Profile.objects.filter()
    serializer_class = local_serializers.ProfileSerializer
    lookup_field = "username"
    filter_backends = [ProfileSearchFilter, filters.OrderingFilter]
    relation_fields = ["departments", "leader", "login_set"]

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
            domain = get_default_category_domain_from_local_cache()
            # domain = ProfileCategory.objects.get(default=True).domain

        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {"username": username, "domain": domain}
        obj = get_object_or_404(queryset, **filter_kwargs)

        return obj

    def get_serializer_class(self):
        """Serializer 路由"""
        if self.action in ("create", "update", "partial_update"):
            return local_serializers.CreateProfileSerializer
        # NOTE: "list" 比较特殊, 放到self.list方法中处理
        else:
            return self.serializer_class

    def get_serializer_context(self):
        origin = super().get_serializer_context()
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
        query_serializer=AdvancedRetrieveSerializer(),
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

        serializer_class = local_serializers.RapidProfileSerializer

        # NOTE: 用于两套用户管理之间的数据同步
        if settings.SYNC_API_PARAM in request.query_params:
            serializer_class = local_serializers.ForSyncRapidProfileSerializer
            request.META[settings.FORCE_RAW_RESPONSE_HEADER] = "true"

        fields = query_data.get("fields", [])
        if fields:
            self._check_fields(fields)
        else:
            # FIXME: 这里应该用 model 的字段, 并且应该最小集合, 目前全获取, 导致放大(last_login_time/departments等)
            # 这里没传fields默认使用slz.fields是有问题的, 但是先保持接口行为一致, 不动fields声明(新版接口解决)
            fields = serializer_class().fields

        self._ensure_enabled_field(request, fields=fields)

        try:
            queryset = self.filter_queryset(self.get_queryset())
        except Exception:
            logger.exception("failed to query profiles")
            raise error_codes.QUERY_PARAMS_ERROR

        # 提前将关系表拿出来
        # BUG: 这里需要去掉 login_set(百万级的表), 大表会导致prefetch就失败
        # queryset = queryset.prefetch_related(*self.relation_fields)
        queryset = queryset.prefetch_related("departments", "leader")

        # 当用户请求数据时，判断其是否强制输出原始 username
        # if not force_use_raw_username(request): # always be true
        # 直接在 DB 中拼接 username & domain，比在 serializer 中快很多
        if "username" in fields:
            # FIXME: bug here? query profiles from other category, not the default
            # default_domain = ProfileCategory.objects.get_default().domain
            default_domain = get_default_category_domain_from_local_cache()
            # 这里拼装的 username@domain, 没有走到serializer中的get_username
            queryset = queryset.extra(
                select={"username": "if(`domain`= %s, username, CONCAT(username, '@', domain))"},
                select_params=(default_domain,),
            )

        page = self.paginate_queryset(queryset)
        # page may be empty list
        if page is not None:
            # BUG: slz 中的 last_login_time 会导致放大查询, 需要剔除(即, 这个接口将不再支持last_login_time)
            # another two property not in slz fields are: latest_check_time bad_check_cnt
            # if "last_login_time" in fields:
            #     del fields["last_login_time"]

            # BUG: 这里必须显式传递 context给到slz, 下层self.context.get("request") 用到, 判断拼接 username@domain
            # 坑, 修改或重构需要注意; 不要通过这种方式来决定字段格式, 非常容易遗漏
            serializer = serializer_class(page, fields=fields, many=True, context=self.get_serializer_context())
            return self.get_paginated_response(serializer.data)

        fields = [x for x in fields if x in self._get_model_field_names()]
        # 全量数据太大，使用 serializer 效率非常低
        # 由于存在多对多字段，所以返回列表会平铺展示，同一个 username 会多次展示
        # https://docs.djangoproject.com/en/1.11/ref/models/querysets/#values
        data = list(queryset.values(*fields))
        data = [remove_sensitive_fields_for_profile(request, d) for d in data]
        return Response(data=data)

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

        # from bkuser_core.departments.models import Department

        # departments为空, 则绕过了第一次权限控制
        # deps = Department.objects.filter(id__in=validated_data.get("departments", []))
        # for dep in deps:
        #     self.check_object_permissions(request, obj=dep)

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

        # 必须要有这个category的管理权限, 才能添加用户到这个目录下
        # 注意这里 saas 传的 action_id = manage_department, 必须先改成manage_category才能检查category权限
        # request.META[settings.ACTION_ID_HEADER] = IAMAction.MANAGE_CATEGORY.value
        # self.check_object_permissions(request, obj=ProfileCategory.objects.get(pk=validated_data["category_id"]))

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
            serializer.validated_data["category_id"],
            return_raw=True,
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
        except Exception as e:
            username = f"{serializer.validated_data['username']}@{serializer.validated_data['domain']}"
            logger.exception(f"failed to create profile<{username}>")
            raise error_codes.SAVE_USER_INFO_FAILED.f(exception_message=e)

        # 善后工作
        post_profile_create.send(
            sender=self,
            instance=instance,
            operator=request.operator,
            extra_values=create_summary,
        )
        return Response(self.serializer_class(instance).data, status=status.HTTP_201_CREATED)

    @method_decorator(clear_cache_if_succeed)
    def _update(self, request, partial):
        instance = self.get_object()
        serializer = local_serializers.UpdateProfileSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        operate_type = OperationType.UPDATE.value

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

    @swagger_auto_schema(
        query_serializer=AdvancedRetrieveSerializer(),
        request_body=local_serializers.UpdateProfileSerializer,
        responses={"200": local_serializers.ProfileSerializer()},
    )
    def update(self, request, *args, **kwargs):
        """更新用户"""
        return self._update(request, partial=False)

    @swagger_auto_schema(
        query_serializer=AdvancedRetrieveSerializer(),
        request_body=local_serializers.UpdateProfileSerializer,
        responses={"200": local_serializers.ProfileSerializer()},
    )
    def partial_update(self, request, *args, **kwargs):
        """更新用户部分字段"""
        return self._update(request, partial=True)

    @swagger_auto_schema(
        query_serializer=AdvancedRetrieveSerializer(),
        request_body=local_serializers.UpdateProfileLanguageSerializer,
        responses={"200": Response()},
    )
    def update_language(self, request, *args, **kwargs):
        """更新用户语言"""
        instance = self.get_object()
        serializer = local_serializers.UpdateProfileLanguageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # 更新
        instance.language = validated_data["language"]
        instance.save(update_fields=["update_time", "language"])

        create_general_log(
            operator=request.operator,
            operate_type=OperationType.UPDATE.value,
            operator_obj=instance,
            request=request,
        )
        return Response()

    @swagger_auto_schema(query_serializer=AdvancedRetrieveSerializer())
    def destroy(self, request, *args, **kwargs):
        """删除用户
        目前采用软删除
        """
        return super().destroy(request, *args, **kwargs)


class LeaderEdgeViewSet(AdvancedModelViewSet, AdvancedListAPIView):
    """上级边"""

    queryset = LeaderThroughModel.objects.filter(to_profile__enabled=True, from_profile__enabled=True)
    serializer_class = local_serializers.LeaderEdgeSerializer
    ordering = ["id"]
