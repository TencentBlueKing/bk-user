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
from typing import Dict, List

from rest_framework import generics
from rest_framework.response import Response

from bkuser.apis.open_v2.mixins import LegacyOpenApiCommonMixin
from bkuser.apis.open_v2.serializers import (
    DepartmentProfileRelationListInputSLZ,
    DepartmentProfileRelationListOutputSLZ,
    ProfileLeaderRelationListInputSLZ,
    ProfileLeaderRelationListOutputSLZ,
)
from bkuser.apps.data_source.models import DataSourceDepartmentUserRelation, DataSourceUserLeaderRelation
from bkuser.apps.tenant.models import TenantDepartment, TenantUser
from bkuser.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum


class DepartmentProfileRelationListApi(LegacyOpenApiCommonMixin, generics.ListAPIView):
    queryset = DataSourceDepartmentUserRelation.objects.only("id", "department_id", "user_id").all()
    cache_key = "list_department_profile_relations"
    cache_timeout = 60 * 10

    def get(self, request, *args, **kwargs):
        slz = DepartmentProfileRelationListInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        if slz.validated_data["no_page"]:
            return self._get_with_no_page()

        return self._get_with_page()

    def _get_with_page(self):
        """分页获取部门用户关系数据，无缓存"""
        relations = self._convert(
            [
                {"id": rel.id, "department_id": rel.department_id, "profile_id": rel.user_id}
                for rel in self.paginate_queryset(self.get_queryset())
            ]
        )
        return self.get_paginated_response(DepartmentProfileRelationListOutputSLZ(relations, many=True).data)

    def _get_with_no_page(self):
        """支持不分页的数据拉取，需要支持 Redis 缓存结果，出于性能考虑，不使用 OutputSLZ"""
        cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.API_RESP_DATA)
        # 如果缓存中存在，则直接返回
        if relations := cache.get(self.cache_key):
            return Response(relations)

        relations = self._convert(
            [
                {"id": rel.id, "department_id": rel.department_id, "profile_id": rel.user_id}
                for rel in self.get_queryset()
            ]
        )
        cache.set(self.cache_key, relations, timeout=self.cache_timeout)
        return Response(relations)

    def _convert(self, data_source_dept_user_relations: List[Dict]) -> List[Dict]:
        """将数据源部门 ID / 数据源用户 ID 转换成租户部门 ID / 租户用户 ID"""
        user_id_map = dict(
            TenantUser.objects.filter(
                data_source_user_id__in=[rel["profile_id"] for rel in data_source_dept_user_relations],
            ).values_list("data_source_user_id", "id")
        )
        dept_id_map = dict(
            TenantDepartment.objects.filter(
                data_source_department_id__in=[rel["department_id"] for rel in data_source_dept_user_relations],
            ).values_list("data_source_department_id", "id")
        )
        return [
            {
                "id": rel["id"],
                "department_id": dept_id_map[rel["department_id"]],
                "profile_id": user_id_map[rel["profile_id"]],
            }
            for rel in data_source_dept_user_relations
            if rel["department_id"] in dept_id_map and rel["profile_id"] in user_id_map
        ]


class ProfileLeaderRelationListApi(LegacyOpenApiCommonMixin, generics.ListAPIView):
    queryset = DataSourceUserLeaderRelation.objects.only("id", "user_id", "leader_id").all()
    cache_key = "list_profile_leader_relations"
    cache_timeout = 60 * 10

    def get(self, request, *args, **kwargs):
        slz = ProfileLeaderRelationListInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        if slz.validated_data["no_page"]:
            return self._get_with_no_page()

        return self._get_with_page()

    def _get_with_page(self):
        """分页获取用户 - Leader 关系数据，无缓存"""
        relations = self._convert(
            [
                {"id": rel.id, "from_profile_id": rel.user_id, "to_profile_id": rel.leader_id}
                for rel in self.paginate_queryset(self.get_queryset())
            ]
        )
        return self.get_paginated_response(ProfileLeaderRelationListOutputSLZ(relations, many=True).data)

    def _get_with_no_page(self):
        """支持不分页的数据拉取，需要支持 Redis 缓存结果，出于性能考虑，不使用 OutputSLZ"""
        cache = Cache(CacheEnum.REDIS, CacheKeyPrefixEnum.API_RESP_DATA)
        # 如果缓存中存在，则直接返回
        if relations := cache.get(self.cache_key):
            return Response(relations)

        relations = self._convert(
            [
                {"id": rel.id, "from_profile_id": rel.user_id, "to_profile_id": rel.leader_id}
                for rel in self.get_queryset()
            ]
        )
        cache.set(self.cache_key, relations, timeout=self.cache_timeout)
        return Response(relations)

    def _convert(self, data_source_user_leader_relations: List[Dict]) -> List[Dict]:
        """将数据源用户 ID 转换为租户用户 ID"""
        data_source_user_ids = set()
        for rel in data_source_user_leader_relations:
            data_source_user_ids.add(rel["from_profile_id"])
            data_source_user_ids.add(rel["to_profile_id"])

        # {data_source_user_id: tenant_user_id}
        user_id_map = dict(
            TenantUser.objects.filter(
                data_source_user_id__in=data_source_user_ids,
            ).values_list("data_source_user_id", "id")
        )
        return [
            {
                "id": rel["id"],
                "from_profile_id": user_id_map[rel["from_profile_id"]],
                "to_profile_id": user_id_map[rel["to_profile_id"]],
            }
            for rel in data_source_user_leader_relations
            if rel["from_profile_id"] in user_id_map and rel["to_profile_id"] in user_id_map
        ]
