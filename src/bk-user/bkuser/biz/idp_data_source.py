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
from typing import List

from django.db import transaction
from django.utils.translation import gettext_lazy as _

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.idp.data_models import (
    DataSourceMatchRule,
    gen_data_source_match_rule_of_local,
)
from bkuser.apps.idp.models import Idp, IdpDataSourceRelation
from bkuser.common.error_codes import error_codes
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.idp_plugins.local.plugin import LocalIdpPluginConfig


class IdpDataSourceRelationHandler:
    """认证源与数据源关系处理器"""

    @staticmethod
    def _build_match_rule(relation: IdpDataSourceRelation) -> DataSourceMatchRule:
        """从关系记录还原出数据源匹配规则对象"""
        return DataSourceMatchRule(
            data_source_id=relation.data_source_id,
            field_compare_rules=relation.field_compare_rules,
        )

    @staticmethod
    def get_real_idp_ids(
        owner_tenant_id: str, idp_plugin_id: str | None = None, data_source_plugin_id: str | None = None
    ) -> List[str]:
        """获取租户下关联了实名数据源的 IDP ID 列表，可按 IDP 插件和数据源插件过滤"""
        relation_filter = {
            "idp_owner_tenant_id": owner_tenant_id,
            "data_source__type": DataSourceTypeEnum.REAL,
        }
        if data_source_plugin_id:
            relation_filter["data_source__plugin_id"] = data_source_plugin_id

        idp_ids = IdpDataSourceRelation.objects.filter(**relation_filter).values_list("idp_id", flat=True).distinct()

        queryset = Idp.objects.filter(id__in=idp_ids, owner_tenant_id=owner_tenant_id)
        if idp_plugin_id:
            queryset = queryset.filter(plugin_id=idp_plugin_id)

        return list(queryset.values_list("id", flat=True))

    @staticmethod
    def get_real_idp_ids_with_orphan(owner_tenant_id: str) -> List[str]:
        """获取租户下关联实名数据源的 IDP 以及孤儿 IDP（无任何关系记录）的 ID 列表。

        与 IDP 关联的所有数据源被删除后，IDP 会变成无关系的孤儿态，仍需返回以便管理员后续重新配置。
        由于 IDP 不会同时关联多种类型的数据源，排除仅关联非实名数据源的 IDP 即可。
        """
        non_real_idp_ids = (
            IdpDataSourceRelation.objects.filter(idp_owner_tenant_id=owner_tenant_id)
            .exclude(data_source__type=DataSourceTypeEnum.REAL)
            .values_list("idp_id", flat=True)
        )
        return list(
            Idp.objects.filter(owner_tenant_id=owner_tenant_id)
            .exclude(id__in=non_real_idp_ids)
            .values_list("id", flat=True)
        )

    @staticmethod
    def get_real_match_rules(idp: Idp) -> List[DataSourceMatchRule]:
        """返回 IDP 全部 REAL 关系（生效范围），供详情回显"""
        return [
            IdpDataSourceRelationHandler._build_match_rule(rel)
            for rel in IdpDataSourceRelation.objects.filter(
                idp=idp, data_source__type=DataSourceTypeEnum.REAL
            ).order_by("created_at", "id")
        ]

    @staticmethod
    def has_duplicate_plugin_real_relation(owner_tenant_id: str, idp_plugin_id: str) -> bool:
        """针对实名数据源，每种 IDP 插件只允许一个 IDP；本方法用于新建时的唯一性校验。

        返回 True（拒绝创建）的两种情形：
        1) 同插件类型的 IDP 已关联实名数据源；
        2) 同插件类型存在孤儿 IDP（无任何关系记录，通常是实名数据源被删除后遗留的），
           仍占据插件槽位，需走更新流程。
        仅关联虚拟数据源的 IDP 不受此约束。

        注意：孤儿 IDP 几乎都源自实名数据源删除（虚拟数据源和内置管理数据源不会产生孤儿），
        因此对孤儿一律拦截，避免重复创建同插件类型的 IDP。
        """
        # 查询同插件类型的 IDP，可能包括已关联实名数据源的、孤儿 IDP、关联内置管理数据源的
        idp_ids = list(
            Idp.objects.filter(owner_tenant_id=owner_tenant_id, plugin_id=idp_plugin_id).values_list("id", flat=True)
        )
        if not idp_ids:
            return False

        # 查询同插件类型的 IDP 是否已关联实名数据源
        has_real_relation = IdpDataSourceRelation.objects.filter(
            idp_owner_tenant_id=owner_tenant_id,
            idp_id__in=idp_ids,
            data_source__type=DataSourceTypeEnum.REAL,
        ).exists()
        if has_real_relation:
            return True

        # 查询同插件类型的 IDP 是否存在孤儿（无任何关系记录）
        related_idp_ids = set(
            IdpDataSourceRelation.objects.filter(idp_id__in=idp_ids).values_list("idp_id", flat=True).distinct()
        )
        return bool(set(idp_ids) - related_idp_ids)

    @staticmethod
    def has_local_idp_relation(data_source: DataSource) -> bool:
        """检查数据源是否被本地认证源关联"""
        return IdpDataSourceRelation.objects.filter(
            data_source=data_source, idp__plugin_id=BuiltinIdpPluginEnum.LOCAL
        ).exists()

    @staticmethod
    def _get_relation_data_source_type(idp: Idp) -> str | None:
        """获取 IDP 当前关联的数据源类型，无任何关系时返回 None。"""
        return IdpDataSourceRelation.objects.filter(idp=idp).values_list("data_source__type", flat=True).first()

    @staticmethod
    def _refresh_local_plugin_config(idp: Idp, data_source_ids: List[int] | None = None) -> None:
        """刷新本地登录插件配置

        仅对本地登录源生效；非本地插件静默跳过。
        关系变更（增/删/刷新）后应始终调用此方法，以保持插件配置与关系表一致。
        :param data_source_ids: 数据源 ID 列表，None 表示从关系表中获取
        """
        if idp.plugin_id != BuiltinIdpPluginEnum.LOCAL:
            return

        if data_source_ids is None:
            data_source_ids = list(
                IdpDataSourceRelation.objects.filter(idp=idp).values_list("data_source_id", flat=True)
            )

        idp.set_plugin_cfg(LocalIdpPluginConfig(data_source_ids=data_source_ids))

    @staticmethod
    @transaction.atomic()
    def set_real_relations_from_match_rules(idp: Idp, match_rules: List[DataSourceMatchRule]) -> None:
        """按显式生效范围刷新 IDP 的实名数据源关系（新增/更新/删除）。

        - 只处理 REAL 数据源关系，虚拟/内置管理关系不受影响
        - match_rules 为空表示清空生效范围（IDP 变孤儿）
        """
        target = {
            rule.data_source_id: [compare_rule.model_dump() for compare_rule in rule.field_compare_rules]
            for rule in match_rules
        }
        IdpDataSourceRelation.objects.filter(idp=idp, data_source__type=DataSourceTypeEnum.REAL).delete()
        IdpDataSourceRelation.objects.bulk_create(
            [
                IdpDataSourceRelation(
                    idp=idp,
                    data_source_id=data_source_id,
                    field_compare_rules=field_compare_rules,
                    idp_owner_tenant_id=idp.owner_tenant_id,
                )
                for data_source_id, field_compare_rules in target.items()
            ]
        )
        IdpDataSourceRelationHandler._refresh_local_plugin_config(idp, list(target.keys()))

    @staticmethod
    @transaction.atomic()
    def remove_data_source_relations(data_source: DataSource) -> None:
        """删除指定数据源的全部认证源关系，并同步受影响的本地登录插件配置。

        本地认证源的 data_source_ids 是关系的冗余，关系删除后必须写回。
        因此不能依赖删除数据源时的 CASCADE, 需在删除数据源前显式调用。
        没有剩余关系的认证源会保留为孤儿态。
        """
        relation = (
            IdpDataSourceRelation.objects.filter(data_source=data_source, idp__plugin_id=BuiltinIdpPluginEnum.LOCAL)
            .select_related("idp")
            .first()
        )
        IdpDataSourceRelation.objects.filter(data_source=data_source).delete()

        if relation:
            IdpDataSourceRelationHandler._refresh_local_plugin_config(relation.idp)

    @staticmethod
    @transaction.atomic()
    def set_builtin_management_relation(idp: Idp, data_source: DataSource) -> None:
        """为内置管理登录源设置唯一的数据源关系（先清除再创建），用于租户初始化流程"""
        if IdpDataSourceRelationHandler._get_relation_data_source_type(idp) == DataSourceTypeEnum.REAL:
            raise error_codes.DATA_SOURCE_OPERATION_UNSUPPORTED.f(
                _("已关联实名数据源的登录源不允许关联内置管理数据源")
            )

        IdpDataSourceRelation.objects.filter(
            idp=idp,
            data_source__type=DataSourceTypeEnum.BUILTIN_MANAGEMENT,
        ).delete()
        IdpDataSourceRelation.objects.create(
            idp=idp,
            data_source=data_source,
            idp_owner_tenant_id=idp.owner_tenant_id,
            field_compare_rules=[
                rule.model_dump() for rule in gen_data_source_match_rule_of_local(data_source.id).field_compare_rules
            ],
        )
        IdpDataSourceRelationHandler._refresh_local_plugin_config(idp)
