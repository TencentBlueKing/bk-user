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
import operator
from collections import defaultdict
from functools import reduce
from typing import Any, Dict, List, Tuple

import phonenumbers
from django.db.models import Q, QuerySet
from django.http import Http404
from rest_framework import generics
from rest_framework.response import Response

from bkuser.apis.open_v2.mixins import LegacyOpenApiCommonMixin
from bkuser.apis.open_v2.pagination import LegacyOpenApiPagination
from bkuser.apis.open_v2.serializers.profilers import (
    DepartmentProfileListInputSLZ,
    ProfileListInputSLZ,
    ProfileRetrieveInputSLZ,
)
from bkuser.apps.data_source.models import (
    DataSourceDepartmentRelation,
    DataSourceDepartmentUserRelation,
    DataSourceUserLeaderRelation,
)
from bkuser.apps.tenant.models import DataSourceDepartment, TenantDepartment, TenantUser
from bkuser.biz.tenant import TenantUserHandler
from bkuser.utils.tree import Tree


def _phone_country_code_to_iso_code(phone_country_code: str) -> str:
    """将 86 等手机国际区号 转换 CN 的 ISO 代码"""
    if phone_country_code and phone_country_code.isdigit():
        return phonenumbers.region_code_for_country_code(int(phone_country_code))

    return ""


class TenantUserListToUserInfosMixin:
    """将 TenantUser 列表转换 对外的用户信息"""

    def build_user_infos(self, tenant_users: QuerySet[TenantUser], fields: List[str]) -> List[Dict[str, Any]]:
        """
        构建对外用户信息列表
        :param tenant_users: 租户用户 Queryset，即已经经过 filter 等后的 QuerySet
                             且必须保证 select_related("data_source_user")
        :param fields: 对外的用户字段列表，空时表示所有用户字段都对外
        """
        # 按需提前获取用户 Leader 信息 和 用户部门信息
        data_source_user_ids = [i.data_source_user.id for i in tenant_users]
        leader_map = self._get_leader_map(data_source_user_ids) if not fields or "leader" in fields else {}
        department_map = (
            self._get_department_map(data_source_user_ids) if not fields or "departments" in fields else {}
        )

        user_infos = []
        for tenant_user in tenant_users:
            # 手机号和手机区号
            phone, phone_country_code = tenant_user.phone_info

            # 不会放大查询的字段
            user_info = {
                # TODO 目前 ID 指的是数据源用户 ID，未来支持协同之后，需要重新考虑
                "id": tenant_user.data_source_user.id,
                # 租户用户 ID 即为对外的 username / bk_username
                "username": tenant_user.id,
                "display_name": TenantUserHandler().generate_tenant_user_display_name(tenant_user),
                "email": tenant_user.email,
                "telephone": phone,
                "country_code": phone_country_code,
                "iso_code": _phone_country_code_to_iso_code(phone_country_code),
                "time_zone": tenant_user.time_zone,
                "language": tenant_user.language,
                "wx_userid": tenant_user.wx_userid,
                "domain": tenant_user.data_source.domain,
                "category_id": tenant_user.data_source_id,
                # TODO 1. 支持软删除后需要特殊处理 2. 支持状态时需要特殊处理
                "status": "",
                "staff_status": "",
                "enabled": True,
                # TODO: 协同时需要调整为按照协同租户配置的用户自定义字段进行输出
                "extras": tenant_user.data_source_user.extras,
                # 总是返回固定值
                "logo": "",
                "position": 0,
            }

            # 指定对外字段，则只返回指定的字段
            if fields:
                user_info = {k: v for k, v in user_info.items() if k in fields}
                # 由于 leader 需要额外计算，因此特殊分支处理
                if "leader" in fields:
                    user_info["leader"] = leader_map.get((tenant_user.tenant.id, tenant_user.data_source_user.id))
                # 由于 department 需要额外计算，因此特殊分支处理
                if "departments" in fields:
                    user_info["departments"] = department_map.get(
                        (tenant_user.tenant.id, tenant_user.data_source_user.id)
                    )

                user_infos.append(user_info)
                continue

            # 未指定字段，则关联字段也要返回
            user_info["leader"] = leader_map.get((tenant_user.tenant.id, tenant_user.data_source_user.id))
            user_info["departments"] = department_map.get((tenant_user.tenant.id, tenant_user.data_source_user.id))

            user_infos.append(user_info)

        return user_infos

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
        # { "数据源 Leader ID": List[租户 Leader ] }， 协同场景下，会出现一个 data_source_user 可以对应多个租户用户
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
                        "display_name": TenantUserHandler().generate_tenant_user_display_name(tenant_leader),
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
                        # TODO: 协同时，是以”伪根“开始，并不是原始数据源的根，需要调整
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


class ProfileListApi(LegacyOpenApiCommonMixin, generics.ListAPIView, TenantUserListToUserInfosMixin):
    """用户列表"""

    pagination_class = LegacyOpenApiPagination

    def get(self, request, *args, **kwargs):
        slz = ProfileListInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        # 根据参数过滤
        tenant_users = self._filter_queryset(params)
        if not params["no_page"]:
            tenant_users = self.paginate_queryset(tenant_users)

        # 根据 fields 构造对外的用户信息
        return Response(self.build_user_infos(tenant_users, params.get("fields")))

    def _filter_queryset(self, params: Dict[str, Any]) -> QuerySet[TenantUser]:
        """根据参数过滤, 生成 TenantUser QuerySet"""
        # Note: 由于对外很多字段都是继承于数据源用户字段，所以这里直接关联查询 data_source_user
        queryset = TenantUser.objects.select_related("data_source_user").distinct()
        # 过滤查询的字段
        lookup_field = params.get("lookup_field")
        if not lookup_field:
            return queryset

        # 构造过滤条件的 Django Queryset Filter
        target_lookups = []
        if exact_lookups := params.get("exact_lookups"):
            # 手机号和邮件，并不是一定继承数据源用户，还有自定义，所以需要多条件过滤，这里单独处理
            if lookup_field in ["email", "phone"]:
                target_lookups = [
                    self._convert_optional_inherited_lookup_field(lookup_field, x, is_exact=True)
                    for x in exact_lookups
                ]
            else:
                # 单一条件通用转换处理
                target_lookups = [Q(**{self._convert_lookup_field(lookup_field): x}) for x in exact_lookups]
        elif fuzzy_lookups := params.get("fuzzy_lookups"):
            # 手机号和邮件，并不是一定继承数据源用户，还有自定义，所以需要多条件过滤，这里单独处理
            if lookup_field in ["email", "phone"]:
                target_lookups = [
                    self._convert_optional_inherited_lookup_field(lookup_field, x, is_exact=False)
                    for x in fuzzy_lookups
                ]
            elif lookup_field == "create_time":
                # create_time 比较特殊，只针对 IAM 提供，特殊条件处理
                target_lookups = self._convert_create_time_lookup_field(fuzzy_lookups)
            else:
                # 单一条件通用转换处理
                target_lookups = [Q(**{self._convert_lookup_field(lookup_field): x}) for x in fuzzy_lookups]

        if target_lookups:
            return queryset.filter(reduce(operator.or_, target_lookups))

        return queryset

    @staticmethod
    def _convert_lookup_field(lookup_field: str) -> str:
        if lookup_field == "id":
            return f"data_source_user__{lookup_field}"
        if lookup_field == "username":
            return "id"
        if lookup_field == "display_name":
            # Q: 为什么 display_name 使用 full_name 查询
            # A: display_name 在旧版本实际上是姓名，所以这里直接使用 full_name
            # TODO: 新版本 display_name 未来支持表达式，需要重新修改，根据表达式来生成
            return "data_source_user__full_name"
        if lookup_field == "wx_userid":
            return "wx_userid"
        if lookup_field == "domain":
            return "data_source__domain"
        if lookup_field == "category_id":
            # TODO 考虑协同的情况
            return "data_source_id"
        if lookup_field in ["enabled", "status", "staff_status"]:
            # FIXME (su) 支持 enabled / status / staff_status 参数
            raise ValueError("lookup field enabled / status / staff_status is not supported now")

        raise ValueError(f"unsupported lookup field: {lookup_field}")

    @staticmethod
    def _convert_create_time_lookup_field(values: List[str]) -> Q:
        """create_time 字段过滤条件，是 IAM 定制的，查询 start_time ~ start_time + X 内创建的用户
        IAM 代码：https://github.com/TencentBlueKing/bk-iam-saas/blob/e2f585b8d66ccbaa529b56c1058ba77f774fb8eb/saas/backend/component/usermgr.py#L64C16-L64C16
        """
        datetime_values = [datetime.datetime.strptime(v, "%Y-%m-%d %H:%M") for v in values]
        # 判断是否满足间隔一分钟
        start_time = datetime_values[0]
        if all(start_time + datetime.timedelta(minutes=idx) == i for idx, i in enumerate(datetime_values)):
            return Q(
                create_time__gte=datetime_values[0],
                create_time__lt=datetime_values[-1] + datetime.timedelta(minutes=1),
            )

        raise ValueError("unsupported lookup field: create_time")

    @staticmethod
    def _convert_optional_inherited_lookup_field(lookup_field: str, value: str, is_exact: bool = True) -> Q:
        """对于可选是否继承数据源用户的字段，构造对应的查询条件，比如 email 和 phone"""
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


class ProfileRetrieveApi(LegacyOpenApiCommonMixin, generics.RetrieveAPIView):
    """查询单个用户"""

    def get(self, request, *args, **kwargs):
        slz = ProfileRetrieveInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        # 路径参数
        lookup_value = kwargs["lookup_value"]
        # TODO (su) 支持软删除后需要根据 include_disabled 参数修改 filters
        if params["lookup_field"] == "username":
            # username 其实就是新的租户用户 ID，形式如 admin / admin@qq.com / uuid4
            filters = {"id": lookup_value}
        else:
            # TODO 目前 ID 指的是数据源用户 ID，未来支持协同之后，需要重新考虑
            filters = {"data_source_user__id": lookup_value}

        # TODO (su) 支持软删除后，需要根据 include_disabled 参数判断是返回被删除的部门还是 Raise 404
        tenant_user = TenantUser.objects.select_related("data_source_user").filter(**filters).first()
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
                "display_name": TenantUserHandler().generate_tenant_user_display_name(i),
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
            tenant=tenant_user.tenant, data_source_department_id__in=department_ids
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

        user_info = {
            # TODO 目前 ID 指的是数据源用户 ID，未来支持协同之后，需要重新考虑
            "id": tenant_user.data_source_user.id,
            # 租户用户 ID 即为对外的 username / bk_username
            "username": tenant_user.id,
            "display_name": TenantUserHandler().generate_tenant_user_display_name(tenant_user),
            "email": tenant_user.email,
            "telephone": phone,
            "country_code": phone_country_code,
            "iso_code": iso_code,
            "time_zone": tenant_user.time_zone,
            "language": tenant_user.language,
            "wx_userid": tenant_user.wx_userid,
            "wx_openid": tenant_user.wx_openid,
            "domain": tenant_user.data_source.domain,
            "category_id": tenant_user.data_source_id,
            # TODO 1. 支持软删除后需要特殊处理 2. 支持状态时需要特殊处理
            "status": "",
            "staff_status": "",
            "enabled": True,
            # TODO: 协同时需要调整为按照协同租户配置的用户自定义字段进行输出
            "extras": tenant_user.data_source_user.extras,
            # 总是返回固定值
            "logo": "",
            "position": 0,
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


class DepartmentProfileListApi(LegacyOpenApiCommonMixin, generics.ListAPIView, TenantUserListToUserInfosMixin):
    """部门下用户"""

    pagination_class = LegacyOpenApiPagination

    def get(self, request, *args, **kwargs):
        slz = DepartmentProfileListInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        params = slz.validated_data

        # TODO (su) 支持软删除后，需要根据 include_disabled 参数判断是返回被删除的部门还是 Raise 404
        tenant_dept = TenantDepartment.objects.filter(id=kwargs["id"]).first()

        if not tenant_dept:
            raise Http404(f"department {kwargs['id']} not found")

        # 根据部门、是否递归，过滤出 部门下的用户
        tenant_users = self._filter_queryset(tenant_dept, params.get("recursive"))
        if not params["no_page"]:
            tenant_users = self.paginate_queryset(tenant_users)

        # 不指定用户字段
        return Response(self.build_user_infos(tenant_users, []))

    @staticmethod
    def _filter_queryset(tenant_dept: TenantDepartment, recursive: bool) -> QuerySet[TenantUser]:
        """根据部门、是否递归，过滤出 部门下的租户用户"""
        # 数据源部门 ID 列表
        dept_ids = [tenant_dept.data_source_department_id]
        if recursive:
            # 根据部门关系，查询部门子孙（包括自身）
            rel = DataSourceDepartmentRelation.objects.filter(department=tenant_dept.data_source_department).first()
            if rel:
                dept_ids = rel.get_descendants(include_self=True).values_list("department_id", flat=True)

        # 查询部门下的用户 ID 列表
        user_ids = DataSourceDepartmentUserRelation.objects.filter(department__in=dept_ids).values_list(
            "user_id", flat=True
        )

        # 租户用户
        return TenantUser.objects.filter(
            tenant_id=tenant_dept.tenant_id, data_source_user_id__in=user_ids
        ).select_related("data_source_user")
