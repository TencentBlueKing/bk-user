# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 Tencent. All rights reserved.
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

import datetime
import operator
from collections import defaultdict
from functools import reduce
from typing import Any, Dict, List, Tuple

import phonenumbers
from blue_krill.data_types.enum import EnumField, StructuredEnum
from django.conf import settings
from django.db.models import Q, QuerySet
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics
from rest_framework.response import Response

from bkuser.apis.open_v2.mixins import DataSourceDomainMixin, DefaultTenantMixin, LegacyOpenApiCommonMixin
from bkuser.apis.open_v2.pagination import LegacyOpenApiPagination
from bkuser.apis.open_v2.serializers.profilers import (
    DepartmentProfileListInputSLZ,
    ProfileLanguageUpdateInputSLZ,
    ProfileListInputSLZ,
    ProfileRetrieveInputSLZ,
)
from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import (
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.tenant.constants import TenantUserStatus
from bkuser.apps.tenant.language import update_tenant_user_language
from bkuser.apps.tenant.models import DataSourceDepartment, TenantDepartment, TenantUser
from bkuser.common.cache import CacheEnum
from bkuser.common.error_codes import error_codes
from bkuser.common.views import ExcludePatchAPIViewMixin
from bkuser.utils.tree import Tree


class ProfileStatusEnum(str, StructuredEnum):
    """2.x 版本 用户状态"""

    NORMAL = EnumField("NORMAL", label="正常")
    LOCKED = EnumField("LOCKED", label="被锁定")
    DELETED = EnumField("DELETED", label="已删除")
    DISABLED = EnumField("DISABLED", label="被禁用")
    EXPIRED = EnumField("EXPIRED", label="已过期")


TENANT_USER_STATUS_TO_PROFILE_STATUS_MAP = {
    TenantUserStatus.ENABLED.value: ProfileStatusEnum.NORMAL.value,
    TenantUserStatus.DISABLED.value: ProfileStatusEnum.DISABLED.value,
    TenantUserStatus.EXPIRED.value: ProfileStatusEnum.EXPIRED.value,
}

PROFILE_STATUS_TO_TENANT_USER_STATUS_MAP = {v: k for k, v in TENANT_USER_STATUS_TO_PROFILE_STATUS_MAP.items()}


def _phone_country_code_to_iso_code(phone_country_code: str) -> str:
    """将 86 等手机国际区号 转换 CN 等 ISO 代码"""
    if phone_country_code and phone_country_code.isdigit():
        return phonenumbers.region_code_for_country_code(int(phone_country_code))

    return ""


class TenantUserListToUserInfosMixin(DefaultTenantMixin, DataSourceDomainMixin):
    """将 TenantUser 列表转换 对外的用户信息"""

    def build_user_infos(self, tenant_users: List[TenantUser], fields: List[str]) -> List[Dict[str, Any]]:
        """
        构建对外用户信息列表
        :param tenant_users: 租户用户 List，即已经经过 filter、only 等优化后的数据
                             select_related 会根据 fields 在 optimize_queryset 中动态添加
        :param fields: 对外的用户字段列表，需要已经标准化处理（调用 _get_default_fields）
        """
        # 批量预加载关联数据
        context = self._prepare_context(tenant_users, fields)

        # 构建每个用户的信息
        return [self._build_single_user_info(tenant_user, fields, context) for tenant_user in tenant_users]

    @staticmethod
    def get_default_fields(fields: List[str]) -> List[str]:
        """获取默认字段列表"""
        return fields or [
            "id",
            "username",
            "display_name",
            "email",
            "telephone",
            "country_code",
            "time_zone",
            "language",
            "wx_userid",
            "domain",
            "category_id",
            "status",
            "extras",
            "position",
            "leader",
            "departments",
        ]

    @staticmethod
    def _get_db_field_map() -> Dict[str, List[str]]:
        """获取字段到数据库字段的映射"""
        return {
            "id": ["data_source_user_id"],
            "username": ["id"],
            "display_name": ["data_source_user__full_name"],
            "email": ["custom_email", "is_inherited_email", "data_source_user__email"],
            "telephone": ["custom_phone", "is_inherited_phone", "data_source_user__phone"],
            "country_code": [
                "custom_phone_country_code",
                "is_inherited_phone",
                "data_source_user__phone_country_code",
            ],
            "time_zone": ["time_zone"],
            "language": ["language"],
            "wx_userid": ["wx_userid"],
            "domain": ["data_source_id", "tenant_id"],
            "category_id": ["data_source_id"],
            "status": ["status"],
            "extras": ["data_source_user__extras", "data_source_id", "tenant_id"],
            "position": ["data_source_user__extras", "data_source_id", "tenant_id"],
            "leader": ["data_source_user_id"],
            "departments": ["data_source_user_id"],
        }

    def optimize_queryset(self, tenant_users: QuerySet[TenantUser], fields: List[str]) -> QuerySet[TenantUser]:
        """优化查询，只查询需要的数据库字段"""
        db_field_map = self._get_db_field_map()
        only_fields = {"id"}
        for f in fields:
            only_fields.update(db_field_map.get(f, []))

        # 根据需要的字段决定是否添加 select_related，避免不必要的关联查询
        # 同时避免 select_related 与 only() 不包含关联字段时的冲突
        if any(field.startswith("data_source_user__") for field in only_fields):
            tenant_users.select_related("data_source_user")

        return tenant_users.only(*only_fields)

    def _prepare_context(self, tenant_users: List[TenantUser], fields: List[str]) -> Dict[str, Any]:
        """预加载关联数据，减少数据库查询"""
        data_source_user_ids = []
        if "leader" in fields or "departments" in fields:
            data_source_user_ids = [i.data_source_user_id for i in tenant_users]

        return {
            "leader_map": self._get_leader_map(data_source_user_ids) if "leader" in fields else {},
            "department_map": self._get_department_map(data_source_user_ids) if "departments" in fields else {},
            "collaboration_field_mapping": (
                self.get_collaboration_field_mapping() if "extras" in fields or "position" in fields else {}
            ),
        }

    def _build_single_user_info(
        self, tenant_user: TenantUser, fields: List[str], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """构建单个用户的信息"""
        user_info: Dict[str, Any] = {}

        # 添加基础字段
        self._add_basic_fields(user_info, tenant_user, fields)

        # 添加电话相关字段
        self._add_phone_fields(user_info, tenant_user, fields)

        # 添加简单字段
        self._add_simple_fields(user_info, tenant_user, fields)

        # 添加自定义字段
        self._add_extras_fields(user_info, tenant_user, fields, context["collaboration_field_mapping"])

        # 添加固定值字段
        user_info["logo"] = ""
        user_info["staff_status"] = "IN"

        # 添加关联字段
        self._add_relation_fields(user_info, tenant_user, fields, context)

        return user_info

    @staticmethod
    def _add_basic_fields(user_info: Dict[str, Any], tenant_user: TenantUser, fields: List[str]) -> None:
        """添加基础字段"""
        if "id" in fields:
            user_info["id"] = tenant_user.data_source_user_id
        if "username" in fields:
            user_info["username"] = tenant_user.id
        if "display_name" in fields:
            user_info["display_name"] = tenant_user.data_source_user.full_name
        if "email" in fields:
            user_info["email"] = tenant_user.email

    @staticmethod
    def _add_phone_fields(user_info: Dict[str, Any], tenant_user: TenantUser, fields: List[str]) -> None:
        """添加电话相关字段"""
        if not any(f in fields for f in ["telephone", "country_code", "iso_code"]):
            return

        phone, phone_country_code = tenant_user.phone_info
        if "telephone" in fields:
            user_info["telephone"] = phone
        if "country_code" in fields:
            user_info["country_code"] = phone_country_code
        if "iso_code" in fields:
            user_info["iso_code"] = _phone_country_code_to_iso_code(phone_country_code)

    def _add_simple_fields(self, user_info: Dict[str, Any], tenant_user: TenantUser, fields: List[str]) -> None:
        """添加简单字段"""
        simple_field_mapping = {
            "time_zone": lambda: tenant_user.time_zone,
            "language": lambda: tenant_user.language,
            "wx_userid": lambda: tenant_user.wx_userid,
            "domain": lambda: self.get_domain(tenant_user.data_source_id, tenant_user.tenant_id),
            "category_id": lambda: tenant_user.data_source_id,
            "status": lambda: TENANT_USER_STATUS_TO_PROFILE_STATUS_MAP.get(tenant_user.status, tenant_user.status),
        }

        for field_name, value_func in simple_field_mapping.items():
            if field_name in fields:
                user_info[field_name] = value_func()

    def _add_extras_fields(
        self,
        user_info: Dict[str, Any],
        tenant_user: TenantUser,
        fields: List[str],
        collaboration_field_mapping: Dict[Tuple[str, str], str],
    ) -> None:
        """添加自定义字段"""
        if not ("extras" in fields or "position" in fields):
            return

        source_extras = tenant_user.data_source_user.extras
        extras = self._get_collaboration_extras(source_extras, tenant_user, collaboration_field_mapping)

        if "extras" in fields:
            user_info["extras"] = extras
        if "position" in fields:
            user_info["position"] = int(source_extras.get("position", 0))

    def _get_collaboration_extras(
        self,
        source_extras: Dict[str, Any],
        tenant_user: TenantUser,
        collaboration_field_mapping: Dict[Tuple[str, str], str],
    ) -> Dict[str, Any]:
        """获取协同场景下的自定义字段"""
        ds_owner_tenant_id = self.data_source_id_to_tenant_id_map()[tenant_user.data_source_id]
        if ds_owner_tenant_id != tenant_user.tenant_id:
            return {
                collaboration_field_mapping[(ds_owner_tenant_id, k)]: v
                for k, v in source_extras.items()
                if (ds_owner_tenant_id, k) in collaboration_field_mapping
            }
        return source_extras

    @staticmethod
    def _add_relation_fields(
        user_info: Dict[str, Any], tenant_user: TenantUser, fields: List[str], context: Dict[str, Any]
    ) -> None:
        """添加关联字段"""
        if "leader" in fields:
            user_info["leader"] = context["leader_map"].get((tenant_user.tenant_id, tenant_user.data_source_user_id))
        if "departments" in fields:
            user_info["departments"] = context["department_map"].get(
                (tenant_user.tenant_id, tenant_user.data_source_user_id)
            )

    @staticmethod
    def _get_leader_map(data_source_user_ids: List[int]) -> Dict[Tuple[str, int], List[Dict[str, Any]]]:
        """
        通过数据源用户 ID 获取其在租户下的 Leader 列表
        : return:
            key = (tenant_id, data_source_user_id)
            value = List[Tenant Leader Info]
        Note: 由于不同用户可能是不同租户的，所以这里只能根据数据源用户查询，
              然后返回数据源用户在每个租户下的 Leader 信息列表
        """
        # 数据源用户 Leader 关系查询
        relations = DataSourceUserLeaderRelation.objects.filter(user_id__in=data_source_user_ids).only(
            "user_id", "leader_id"
        )
        leader_ids = [i.leader_id for i in relations]
        if not leader_ids:
            return {}

        # 查询 Leader 对应的租户用户
        leaders = TenantUser.objects.filter(data_source_user_id__in=leader_ids).select_related("data_source_user")
        # { "数据源 Leader ID": List[租户 Leader ] }，协同场景下，会出现一个 data_source_user 可以对应多个租户用户
        tenant_leader_map = defaultdict(list)
        for i in leaders:
            tenant_leader_map[i.data_source_user_id].append(i)

        # 基于 leader 必须与用户同一个租户才是有效的，这里以 (tenant_id, data_source_user_id) 作为 key
        # { (tenant_id, data_source_user_id) : List[Tenant Leader Info] }
        leader_map = defaultdict(list)
        for rel in relations:
            for tenant_leader in tenant_leader_map[rel.leader_id]:
                leader_map[(tenant_leader.tenant_id, rel.user_id)].append(
                    {
                        "id": tenant_leader.data_source_user.id,
                        "username": tenant_leader.id,
                        "display_name": tenant_leader.data_source_user.full_name,
                    }
                )
        return leader_map

    @staticmethod
    def _get_department_map(data_source_user_ids: List[int]) -> Dict[Tuple[str, int], List[Dict[str, Any]]]:
        """
        通过数据源用户 ID 获取其在租户下的（直属）部门 列表
        """
        # 查询用户所在的数据源部门
        relations = DataSourceDepartmentUserRelation.objects.filter(user_id__in=data_source_user_ids).only(
            "user_id", "department_id"
        )
        department_ids = [i.department_id for i in relations]
        if not department_ids:
            return {}

        # 查询部门对应的租户部门
        tenant_departments = TenantDepartment.objects.filter(
            data_source_department_id__in=department_ids
        ).select_related("data_source_department")
        # { "数据源部门 ID": List[租户部门] } ，协同场景下，可能会出现一个数据源对应多个租户部门
        tenant_dept_map = defaultdict(list)
        for i in tenant_departments:
            tenant_dept_map[i.data_source_department_id].append(i)

        # dept_id_name_map 和 rel_tree 用于计算部门 full_name
        # {数据源部门 ID: 数据源部门名称}
        dept_id_name_map = dict(DataSourceDepartment.objects.values_list("id", "name"))
        rel_tree = Tree(DataSourceDepartmentRelation.objects.values_list("department_id", "parent_id"))

        # 基于 部门 必须与用户同一个租户才是有效的，这里以 (tenant_id, data_source_user_id) 作为 key
        dept_map: Dict[Tuple[str, int], List[Dict]] = defaultdict(list)
        for rel in relations:
            for tenant_dept in tenant_dept_map[rel.department_id]:
                idx = len(dept_map[(tenant_dept.tenant_id, rel.user_id)])
                dept_map[(tenant_dept.tenant_id, rel.user_id)].append(
                    {
                        "id": tenant_dept.id,
                        "name": tenant_dept.data_source_department.name,
                        # TODO: 协同支持指定范围后，是以“伪根”开始，并不是原始数据源的根，需要调整
                        "full_name": "/".join(
                            [
                                dept_id_name_map[i]
                                for i in rel_tree.get_ancestors(
                                    tenant_dept.data_source_department.id, include_self=True
                                )
                            ]
                        ),
                        "order": idx + 1,
                    }
                )

        return dept_map


class ProfileListApi(LegacyOpenApiCommonMixin, TenantUserListToUserInfosMixin, generics.ListAPIView):
    """用户列表"""

    pagination_class = LegacyOpenApiPagination

    @method_decorator(cache_page(cache=CacheEnum.REDIS.value, timeout=settings.OPEN_API_V2_LIST_USER_CACHE_TIMEOUT))
    def get(self, request, *args, **kwargs):
        slz = ProfileListInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data
        no_page = params["no_page"]

        # 根据参数过滤
        tenant_users = self._filter_queryset(params)

        # 在分页前 (不分页也需优化) 进行 queryset 优化（只查询需要的字段）要的字段
        fields = params.get("fields")
        fields = self.get_default_fields(fields)
        tenant_users = self.optimize_queryset(tenant_users, fields)

        if not no_page:
            tenant_users = self.paginate_queryset(tenant_users)

        # 根据 fields 构造对外的用户信息
        user_infos = self.build_user_infos(tenant_users, fields)
        if not no_page:
            return self.get_paginated_response(user_infos)

        return Response(user_infos)

    def _filter_queryset(self, params: Dict[str, Any]) -> QuerySet[TenantUser]:
        """根据参数过滤，生成 TenantUser QuerySet"""
        # 注：兼容 v2 的 OpenAPI 只提供默认租户的数据（包括默认租户本身数据源的数据 & 其他租户协同过来的数据）
        # Note: select_related 会在 optimize_queryset 中根据需要的字段动态添加
        queryset = TenantUser.objects.filter(
            tenant=self.default_tenant, data_source_id__in=self.get_data_source_ids()
        ).order_by("data_source_user_id")
        # 过滤查询的字段
        lookup_field = params.get("lookup_field")
        if not lookup_field:
            return queryset

        # 精确过滤或模糊搜索的值列表，多值是 Or 关系
        lookup_values = params.get("exact_lookups") or params.get("fuzzy_lookups") or []
        if not lookup_values:
            return queryset

        # 构造过滤条件的 Django Queryset Filter
        is_exact = bool(params.get("exact_lookups"))

        target_lookups = self._gen_target_lookups(lookup_field, lookup_values, is_exact)
        if target_lookups is None:
            return TenantUser.objects.none()

        if target_lookups:
            return queryset.filter(reduce(operator.or_, target_lookups))

        return queryset

    def _gen_target_lookups(self, lookup_field: str, lookup_values: List[str], is_exact: bool) -> List[Q] | None:
        """
        根据 lookup_field 和 lookup_values 构造对应的 Django Queryset Filter

        :param lookup_field: 字段名
        :param lookup_values: 字段值列表
        :param is_exact: 是否精确匹配

        :return: 生成的 Django Queryset Filter, None 值表示一定过滤不到，空列表表示无需过滤
        """
        if lookup_field == "staff_status":
            # 员工状态，3.x 所有用户数据都是 IN 状态，无 OUT 状态
            return None if "IN" not in lookup_values else []

        # 手机号和邮件，并不是一定继承数据源用户，还有自定义，所以需要多条件过滤
        if lookup_field in ["email", "telephone"]:
            return [
                self._convert_optional_inherited_lookup_to_query(lookup_field, value, is_exact=is_exact)
                for value in lookup_values
            ]

        # 模糊查询 create_time 比较特殊，只针对 IAM 提供，特殊条件处理
        if lookup_field == "create_time":
            return [self._convert_create_time_lookup_to_query(lookup_values, is_exact=is_exact)]

        # 状态转换
        if lookup_field == "status":
            status_query = self._convert_status_lookup_to_query(lookup_values, is_exact)
            return None if status_query is None else [status_query]

        # Domain 转 数据源 ID
        if lookup_field == "domain":
            domain_query = self._convert_domain_lookup_to_query(lookup_values, is_exact)
            return None if domain_query is None else [domain_query]

        # 通用转换处理
        return [Q(**{self._convert_lookup_field(lookup_field, is_exact=is_exact): x}) for x in lookup_values]

    @staticmethod
    def _convert_lookup_field(lookup_field: str, is_exact: bool = True) -> str:
        """
        Note：部分 Lookup Filed 不支持模糊匹配
        """
        # 支持精确匹配字段
        allowed_exact_lookup_fields = ["id", "username", "display_name", "wx_userid", "category_id"]
        if is_exact and lookup_field not in allowed_exact_lookup_fields:
            raise error_codes.VALIDATION_ERROR.f(f"unsupported exact lookup field: {lookup_field}")

        # 支持模糊匹配字段
        allowed_fuzzy_lookup_fields = ["username", "display_name"]
        if not is_exact and lookup_field not in allowed_fuzzy_lookup_fields:
            raise error_codes.VALIDATION_ERROR.f(f"unsupported fuzzy lookup field: {lookup_field}")

        lookup_field_map = {
            "id": "data_source_user__id",
            "username": "id",
            # Q: 为什么 display_name 使用 full_name 查询
            # A: display_name 在旧版本实际上是姓名，所以这里直接使用 full_name，
            #    后续支持 DisplayName 以 v3 API 为准，v2 兼容接口不支持
            "display_name": "data_source_user__full_name",
            "wx_userid": "wx_userid",
            "category_id": "data_source_id",
        }

        if lookup_field not in lookup_field_map:
            raise error_codes.VALIDATION_ERROR.f(f"unsupported lookup field: {lookup_field}")

        return lookup_field_map[lookup_field] if is_exact else f"{lookup_field_map[lookup_field]}__icontains"

    @staticmethod
    def _convert_status_lookup_to_query(values: List[str], is_exact: bool) -> Q | None:
        """对于状态字段的转换查询"""
        # 不支持模糊查询
        if not is_exact:
            raise error_codes.VALIDATION_ERROR.f("unsupported fuzzy lookup field: status")

        # 2.x 的用户状态转换为 3.x 的用户状态，不存在的状态则忽略
        lookup_values = [
            PROFILE_STATUS_TO_TENANT_USER_STATUS_MAP[v]  # type: ignore
            for v in values
            if v in PROFILE_STATUS_TO_TENANT_USER_STATUS_MAP
        ]
        # 不存在 3.x 状态，则说明查询不到任何用户
        if not lookup_values:
            return None

        return Q(status=lookup_values[0]) if len(lookup_values) == 1 else Q(status__in=lookup_values)

    def _convert_domain_lookup_to_query(self, values: List[str], is_exact: bool) -> Q | None:
        """对于 Domain 字段的转换查询"""
        # 不支持模糊查询
        if not is_exact:
            raise error_codes.VALIDATION_ERROR.f("unsupported fuzzy lookup field: domain")

        # 目标租户为默认租户的所有数据源 domain 映射
        domain_to_data_source_map = {
            domain: ds_id
            for (ds_id, tenant_id), domain in self.data_source_to_domain_map().items()
            if tenant_id == self.default_tenant.id
        }

        # 将 domain 查询转换为 数据源 ID 查询
        lookup_values = [domain_to_data_source_map[v] for v in values if v in domain_to_data_source_map]

        # 不存在，则说明查询不到任何用户
        if not lookup_values:
            return None

        return Q(data_source_id=lookup_values[0]) if len(lookup_values) == 1 else Q(data_source_id__in=lookup_values)

    @staticmethod
    def _convert_create_time_lookup_to_query(values: List[str], is_exact: bool) -> Q:
        """create_time 字段过滤条件，是 IAM 定制的，查询 start_time ~ start_time + X 内创建的用户
        IAM 代码：https://github.com/TencentBlueKing/bk-iam-saas/blob/e2f585b8d66ccbaa529b56c1058ba77f774fb8eb/saas/backend/component/usermgr.py#L64C16-L64C16
        """
        # 不支持精确过滤
        if is_exact:
            raise error_codes.VALIDATION_ERROR.f("unsupported extra lookup field: create_time")

        # 时间转换异常，说明非预期内 IAM 特殊查询数据（从大到小）
        try:
            datetime_values = [
                datetime.datetime.strptime(v, "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc) for v in values
            ]
        except Exception as error:
            raise error_codes.VALIDATION_ERROR.f(f"unsupported fuzzy create_time values: {values}, error={error}")

        # 从小到大
        datetime_values.reverse()

        # 判断是否满足间隔一分钟
        start_time = datetime_values[0]
        if all(start_time + datetime.timedelta(minutes=idx) == i for idx, i in enumerate(datetime_values)):
            return Q(
                created_at__gte=datetime_values[0],
                created_at__lt=datetime_values[-1] + datetime.timedelta(minutes=1),
            )

        raise error_codes.VALIDATION_ERROR.f(f"unsupported fuzzy create_time values: {values}")

    @staticmethod
    def _convert_optional_inherited_lookup_to_query(lookup_field: str, value: str, is_exact: bool) -> Q:
        """对于可选是否继承数据源用户的字段，构造对应的查询条件，比如 email 和 phone"""
        if lookup_field == "telephone":
            lookup_field = "phone"

        # 精确查询
        if is_exact:
            return Q(
                # 继承
                **{f"is_inherited_{lookup_field}": True, f"data_source_user__{lookup_field}": value},
            ) | Q(
                # 自定义
                **{f"is_inherited_{lookup_field}": False, f"custom_{lookup_field}": value},
            )

        # 模糊查询
        return Q(
            # 继承
            **{f"is_inherited_{lookup_field}": True, f"data_source_user__{lookup_field}__icontains": value},
        ) | Q(
            # 自定义
            **{f"is_inherited_{lookup_field}": False, f"custom_{lookup_field}__icontains": value},
        )


class ProfileRetrieveApi(
    LegacyOpenApiCommonMixin, DefaultTenantMixin, DataSourceDomainMixin, generics.RetrieveAPIView
):
    """查询单个用户"""

    def get(self, request, *args, **kwargs):
        slz = ProfileRetrieveInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        lookup_filter: Dict[str, Any] = {}
        if params["lookup_field"] == "username":
            # username 其实就是新的租户用户 ID，形式如 admin / admin@qq.com / uuid4 / nanoid
            lookup_filter["id"] = kwargs["lookup_value"]
        else:
            lookup_filter["data_source_user__id"] = kwargs["lookup_value"]

        # 注：兼容 v2 的 OpenAPI 只提供默认租户的数据（包括默认租户本身数据源的数据 & 其他租户协同过来的数据）
        tenant_user = (
            TenantUser.objects.select_related("data_source_user")
            .filter(
                Q(**lookup_filter),
                Q(tenant_id=self.default_tenant.id),
                Q(data_source_id__in=self.get_data_source_ids()),
            )
            .first()
        )
        if not tenant_user:
            raise Http404(f"user {params['lookup_field']}:{kwargs['lookup_value']} not found")

        # 根据 fields 构造对外的用户信息
        user_info = self._build_user_info(tenant_user, fields=params.get("fields"))

        return Response(user_info)

    @staticmethod
    def _get_leaders(tenant_user: TenantUser) -> List[Dict[str, Any]]:
        """获取单个租户用户的 Leader"""
        # 数据源用户 Leader 关系查询
        leader_ids = list(
            DataSourceUserLeaderRelation.objects.filter(user=tenant_user.data_source_user).values_list(
                "leader_id", flat=True
            )
        )
        if not leader_ids:
            return []

        # 查询 Leader 对应的租户用户
        leaders = TenantUser.objects.filter(
            tenant=tenant_user.tenant, data_source_user_id__in=leader_ids
        ).select_related("data_source_user")

        return [
            {
                "id": i.data_source_user.id,
                "username": i.id,
                "display_name": i.data_source_user.full_name,
            }
            for i in leaders
        ]

    def _get_departments(self, tenant_user: TenantUser) -> List[Dict[str, Any]]:
        """获取单个租户用户的租户部门"""
        # 查询用户所在的数据源部门
        department_ids = DataSourceDepartmentUserRelation.objects.filter(
            user=tenant_user.data_source_user
        ).values_list("department_id", flat=True)
        if not department_ids:
            return []

        # 查询对应的租户部门
        departments = TenantDepartment.objects.filter(
            tenant_id=tenant_user.tenant_id, data_source_department_id__in=department_ids
        ).select_related("data_source_department")

        # 部门的 full_name
        full_name_map = self._get_department_full_name_map(department_ids)

        return [
            {
                "id": dept.id,
                "name": dept.data_source_department.name,
                "full_name": full_name_map.get(dept.data_source_department.id) or dept.data_source_department.name,
                "order": idx,
            }
            for idx, dept in enumerate(departments, start=1)
        ]

    @staticmethod
    def _get_department_full_name_map(department_ids: List[int]) -> Dict[int, str]:
        """获取部门的 full name"""
        # 查询每个数据源部门的 MPTT 关系，用于获取祖先，进而便于后面获取部门的 full_name
        dept_relations = DataSourceDepartmentRelation.objects.filter(department_id__in=department_ids)
        return {
            rel.department_id: "/".join(
                rel.get_ancestors(include_self=True).values_list("department__name", flat=True)
            )
            for rel in dept_relations
        }

    def _build_user_info(self, tenant_user: TenantUser, fields: List[str]) -> Dict[str, Any]:
        """生成用户信息"""
        phone, phone_country_code = tenant_user.phone_info
        iso_code = _phone_country_code_to_iso_code(phone_country_code)

        # 自定义字段
        source_extras = tenant_user.data_source_user.extras
        data_source_owner_tenant_id = tenant_user.data_source.owner_tenant_id
        # 协同时按照协同租户配置的用户自定义字段进行输出
        if data_source_owner_tenant_id != tenant_user.tenant_id:
            collaboration_field_mapping = self.get_collaboration_field_mapping()
            extras = {
                collaboration_field_mapping[(data_source_owner_tenant_id, k)]: v
                for k, v in source_extras.items()
                if (data_source_owner_tenant_id, k) in collaboration_field_mapping
            }
        else:
            extras = source_extras

        user_info = {
            "id": tenant_user.data_source_user.id,
            # 租户用户 ID 即为对外的 username / bk_username
            "username": tenant_user.id,
            "display_name": tenant_user.data_source_user.full_name,
            "email": tenant_user.email,
            "telephone": phone,
            "country_code": phone_country_code,
            "iso_code": iso_code,
            "time_zone": tenant_user.time_zone,
            "language": tenant_user.language,
            "wx_userid": tenant_user.wx_userid,
            "wx_openid": tenant_user.wx_openid,
            "domain": self.get_domain(tenant_user.data_source_id, tenant_user.tenant_id),
            "category_id": tenant_user.data_source_id,
            "status": TENANT_USER_STATUS_TO_PROFILE_STATUS_MAP.get(tenant_user.status, tenant_user.status),
            "enabled": True,
            "extras": extras,
            "position": int(source_extras.get("position", 0)),
            # 总是返回固定值
            "staff_status": "IN",
            "logo": "",
            "type": "",
            "role": 0,
        }

        # 指定字段
        if fields:
            user_info = {k: v for k, v in user_info.items() if k in fields}
            # 由于 leader 需要额外计算，因此特殊分支处理
            if "leader" in fields:
                user_info["leader"] = self._get_leaders(tenant_user)
            # 由于 department 需要额外计算，因此特殊分支处理
            if "departments" in fields:
                user_info["departments"] = self._get_departments(tenant_user)

            return user_info

        # 无指定，则关联关系字段也需要返回
        user_info["leader"] = self._get_leaders(tenant_user)
        user_info["departments"] = self._get_departments(tenant_user)

        return user_info


class DepartmentProfileListApi(LegacyOpenApiCommonMixin, TenantUserListToUserInfosMixin, generics.ListAPIView):
    """部门下用户"""

    pagination_class = LegacyOpenApiPagination

    def get(self, request, *args, **kwargs):
        slz = DepartmentProfileListInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data
        no_page = params["no_page"]

        tenant_dept = TenantDepartment.objects.filter(
            id=kwargs["id"], tenant=self.default_tenant, data_source__type=DataSourceTypeEnum.REAL
        ).first()
        if not tenant_dept:
            raise Http404(f"department {kwargs['id']} not found")

        # 根据部门、是否递归，过滤出 部门下的用户
        tenant_users = self._filter_queryset(tenant_dept, params.get("recursive"))

        # 在分页前 (不分页也需优化) 进行 queryset 优化（只查询需要的字段）要的字段
        fields = self.get_default_fields([])
        tenant_users = self.optimize_queryset(tenant_users, fields)

        if not no_page:
            tenant_users = self.paginate_queryset(tenant_users)

        # 不指定用户字段
        user_infos = self.build_user_infos(tenant_users, fields)
        if not no_page:
            return self.get_paginated_response(user_infos)

        return Response(user_infos)

    @staticmethod
    def _filter_queryset(tenant_dept: TenantDepartment, recursive: bool) -> QuerySet[TenantUser]:
        """根据部门、是否递归，过滤出 部门下的租户用户"""
        # 数据源部门 ID 列表
        dept_ids = [tenant_dept.data_source_department_id]
        if recursive:
            # 根据部门关系，查询部门子孙（包括自身）
            rel = DataSourceDepartmentRelation.objects.filter(
                department_id=tenant_dept.data_source_department_id
            ).first()
            if rel:
                dept_ids = rel.get_descendants(include_self=True).values_list("department_id", flat=True)

        # 查询部门下的用户 ID 列表
        user_ids = DataSourceDepartmentUserRelation.objects.filter(department_id__in=dept_ids).values_list(
            "user_id", flat=True
        )

        # 租户用户
        # Note: 由于虚拟账号不存在部门关系，所以这里不需要查询虚拟账号情况
        # Note: select_related 会在 optimize_queryset 中根据需要的字段动态添加
        return TenantUser.objects.filter(tenant_id=tenant_dept.tenant_id, data_source_user_id__in=user_ids)


class ProfileLanguageUpdateApi(
    ExcludePatchAPIViewMixin, DefaultTenantMixin, LegacyOpenApiCommonMixin, generics.UpdateAPIView
):
    """更新用户国际化语言"""

    def put(self, request, *args, **kwargs):
        slz = ProfileLanguageUpdateInputSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        tenant_user = TenantUser.objects.filter(
            id=kwargs["username"], tenant=self.default_tenant, data_source_id__in=self.get_data_source_ids()
        ).first()
        if not tenant_user:
            raise Http404(f"user username:{kwargs['username']} not found")

        update_tenant_user_language(tenant_user, slz.validated_data["language"])

        return Response()
