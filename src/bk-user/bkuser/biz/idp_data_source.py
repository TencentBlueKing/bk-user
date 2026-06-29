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
from typing import Any, Dict, List

from django.db import transaction

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.idp.data_models import (
    DataSourceMatchRule,
    gen_data_source_match_rule_of_local,
)
from bkuser.apps.idp.models import Idp, IdpDataSourceRelation
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.idp_plugins.local.plugin import LocalIdpPluginConfig
from bkuser.plugins.constants import DataSourcePluginEnum


# TODO: 待开发产品登录源配置页面支持选择配置多数据源时，重新进行梳理调整和重构
#   重点关注：实名数据源、内置管理数据源、本地数据源、本地登录源的关系和约束
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
    def _get_real_data_source_ids(owner_tenant_id: str, plugin_id: str | None = None) -> List[int]:
        """获取指定租户下全部实名数据源 ID，可按插件类型进一步筛选"""
        queryset = DataSource.objects.filter(owner_tenant_id=owner_tenant_id, type=DataSourceTypeEnum.REAL)
        if plugin_id:
            queryset = queryset.filter(plugin_id=plugin_id)

        return list(queryset.order_by("id").values_list("id", flat=True))

    @staticmethod
    def get_relation_data_source_ids(
        idp: Idp,
        data_source_type: str | None = None,
        data_source_plugin_id: str | None = None,
    ) -> List[int]:
        """获取 IDP 关联的数据源 ID 列表，按关系创建时间排序，保证主数据源排在最前。

        支持按数据源类型和插件 ID 过滤；返回顺序与关系创建顺序一致，
        用于本地登录插件配置等需要稳定排序的场景。
        """
        relation_ids = list(
            IdpDataSourceRelation.objects.filter(idp=idp)
            .order_by("created_at", "id")
            .values_list("data_source_id", flat=True)
        )
        if not relation_ids:
            return []

        data_sources = DataSource.objects.filter(id__in=relation_ids)
        if data_source_type:
            data_sources = data_sources.filter(type=data_source_type)
        if data_source_plugin_id:
            data_sources = data_sources.filter(plugin_id=data_source_plugin_id)

        data_source_ids = set(data_sources.values_list("id", flat=True))
        return [data_source_id for data_source_id in relation_ids if data_source_id in data_source_ids]

    @staticmethod
    def get_related_real_data_sources(idp: Idp, data_source_plugin_id: str | None = None) -> List[DataSource]:
        """获取 IDP 关联的全部实名数据源对象，按关系创建顺序排列"""
        data_source_ids = IdpDataSourceRelationHandler.get_relation_data_source_ids(
            idp,
            data_source_type=DataSourceTypeEnum.REAL,
            data_source_plugin_id=data_source_plugin_id,
        )
        if not data_source_ids:
            return []

        data_source_map = DataSource.objects.in_bulk(data_source_ids)
        return [
            data_source_map[data_source_id] for data_source_id in data_source_ids if data_source_id in data_source_map
        ]

    @staticmethod
    def get_primary_real_match_rule(idp: Idp) -> DataSourceMatchRule | None:
        """获取 IDP 最早建立的实名数据源匹配规则，用于页面回显和登录匹配模板展示"""
        relation = (
            IdpDataSourceRelation.objects.filter(idp=idp, data_source__type=DataSourceTypeEnum.REAL)
            .order_by("id")
            .first()
        )
        if relation is None:
            return None

        return IdpDataSourceRelationHandler._build_match_rule(relation)

    @staticmethod
    def get_primary_real_data_source(idp: Idp, data_source_plugin_id: str | None = None) -> DataSource | None:
        """获取 IDP 关联的首个（主）实名数据源，无关联时返回 None"""
        data_sources = IdpDataSourceRelationHandler.get_related_real_data_sources(
            idp, data_source_plugin_id=data_source_plugin_id
        )
        return data_sources[0] if data_sources else None

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

        数据源被重置但保留登录源时，IDP 会变成无关系的孤儿态，仍需返回以便管理员后续重新配置。
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
    def has_duplicate_plugin_real_relation(owner_tenant_id: str, idp_plugin_id: str) -> bool:
        """针对实名数据源，每种 IDP 插件只允许一个 IDP；本方法用于新建时的唯一性校验。

        返回 True（拒绝创建）的两种情形：
        1) 同插件类型的 IDP 已关联实名数据源；
        2) 同插件类型存在孤儿 IDP（无任何关系记录，通常是实名数据源被重置后遗留的），
           仍占据插件槽位，需走更新流程。
        仅关联虚拟数据源的 IDP 不受此约束。

        注意：孤儿 IDP 几乎都源自实名数据源重置（虚拟数据源和内置管理数据源不会产生孤儿），
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
    def sync_local_plugin_config(idp: Idp) -> None:
        """将 IDP 当前关联的数据源 ID 同步到本地登录插件配置中。

        仅对本地登录源生效；非本地插件静默跳过。
        关系变更（增/删/刷新）后应始终调用此方法，以保持插件配置与关系表一致。
        """
        if idp.plugin_id != BuiltinIdpPluginEnum.LOCAL:
            return

        idp.set_plugin_cfg(
            LocalIdpPluginConfig(data_source_ids=IdpDataSourceRelationHandler.get_relation_data_source_ids(idp))
        )

    @staticmethod
    @transaction.atomic()
    def set_real_relations_from_match_rules(idp: Idp, field_compare_rules: List[Dict[str, Any]]) -> None:
        """用统一的字段比较规则为当前租户下全部实名数据源刷新 IDP 关系。

        当前产品页面只配置一套字段比较规则，应用到同租户全部实名数据源。
        新增实名数据源后不会自动追加关系，管理员确认数据源 ready 后再次保存
        登录源即可完成覆盖刷新。
        注意：数据源创建流程默认不调用该方法，避免未确认 ready 的实名数据源提前进入登录匹配范围。
        """
        if not field_compare_rules:
            return

        # 获取当前租户下全部实名数据源，无可用数据源则无需处理
        real_data_source_ids = IdpDataSourceRelationHandler._get_real_data_source_ids(idp.owner_tenant_id)
        if not real_data_source_ids:
            return

        # 先删后建：清除旧的实名数据源关系，再为每个实名数据源统一创建新关系
        IdpDataSourceRelation.objects.filter(idp=idp, data_source_id__in=real_data_source_ids).delete()
        IdpDataSourceRelation.objects.bulk_create(
            [
                IdpDataSourceRelation(
                    idp=idp,
                    data_source_id=data_source_id,
                    idp_owner_tenant_id=idp.owner_tenant_id,
                    field_compare_rules=field_compare_rules,
                )
                for data_source_id in real_data_source_ids
            ]
        )

        # 关系变更后同步本地登录插件配置，保持插件配置与关系表一致
        IdpDataSourceRelationHandler.sync_local_plugin_config(idp)

    @staticmethod
    @transaction.atomic()
    def set_local_real_relations(idp: Idp) -> None:
        """为本地登录源自动建立与同租户全部本地实名数据源的关系，并使用默认匹配规则。

        先清除旧关系再全量重建，适用于初始化或数据源变更后的关系重置场景。
        """
        data_source_ids = IdpDataSourceRelationHandler._get_real_data_source_ids(
            idp.owner_tenant_id, plugin_id=DataSourcePluginEnum.LOCAL
        )
        if not data_source_ids:
            return

        IdpDataSourceRelation.objects.filter(idp=idp, data_source_id__in=data_source_ids).delete()
        IdpDataSourceRelation.objects.bulk_create(
            [
                IdpDataSourceRelation(
                    idp=idp,
                    data_source_id=data_source_id,
                    idp_owner_tenant_id=idp.owner_tenant_id,
                    field_compare_rules=[
                        rule.model_dump()
                        for rule in gen_data_source_match_rule_of_local(data_source_id).field_compare_rules
                    ],
                )
                for data_source_id in data_source_ids
            ]
        )
        IdpDataSourceRelationHandler.sync_local_plugin_config(idp)

    @staticmethod
    @transaction.atomic()
    def set_builtin_management_relation(idp: Idp, data_source: DataSource) -> None:
        """为内置管理登录源设置唯一的数据源关系（先清除再创建），用于租户初始化流程"""
        IdpDataSourceRelation.objects.filter(idp=idp).delete()
        IdpDataSourceRelation.objects.create(
            idp=idp,
            data_source=data_source,
            idp_owner_tenant_id=idp.owner_tenant_id,
            field_compare_rules=[
                rule.model_dump() for rule in gen_data_source_match_rule_of_local(data_source.id).field_compare_rules
            ],
        )
        IdpDataSourceRelationHandler.sync_local_plugin_config(idp)
