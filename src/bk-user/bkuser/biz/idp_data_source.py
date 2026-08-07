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
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

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


@dataclass
class IdpDeletionPlan:
    """删除实名数据源时，对相关 IDP 的处置方案"""

    to_delete: List[Idp] = field(default_factory=list)
    to_disable: List[Idp] = field(default_factory=list)
    to_sync_local: List[Idp] = field(default_factory=list)


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
    def get_real_match_rules(idp: Idp) -> List[DataSourceMatchRule]:
        """返回 idp 全部 REAL 关系（生效范围），供详情回显"""
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
    def set_real_relations_from_match_rules(idp: Idp, match_rules: List[DataSourceMatchRule]) -> None:
        """按显式生效范围 diff 刷新 idp 的实名数据源关系（新增/更新/删除）。

        - 只处理 REAL 数据源关系，虚拟/内置管理关系不受影响
        - match_rules 为空表示清空生效范围（idp 变孤儿）
        - 联邦源兼容全部 REAL 源，本地账密只兼容 plugin_id=local
        """
        # 构建目标映射：data_source_id -> field_compare_rules
        target = {rule.data_source_id: [r.model_dump() for r in rule.field_compare_rules] for rule in match_rules}
        target_ids = set(target.keys())

        # 校验目标数据源均属当前租户、为 REAL 类型
        if target_ids:
            valid_qs = DataSource.objects.filter(
                id__in=target_ids, owner_tenant_id=idp.owner_tenant_id, type=DataSourceTypeEnum.REAL
            )
            if idp.plugin_id == BuiltinIdpPluginEnum.LOCAL:
                valid_qs = valid_qs.filter(plugin_id=DataSourcePluginEnum.LOCAL)
            valid_ids = set(valid_qs.values_list("id", flat=True))
            if target_ids - valid_ids:
                raise ValidationError(_("存在不兼容或不属于当前租户的实名数据源"))

        # 现有 REAL 关系: {data_source_id: relation}（target 为空表示清空全部 REAL 关系）
        existing = {
            rel.data_source_id: rel
            for rel in IdpDataSourceRelation.objects.filter(idp=idp, data_source__type=DataSourceTypeEnum.REAL)
        }
        existing_ids = set(existing.keys())

        # 删：现有有，目标无
        if to_delete := existing_ids - target_ids:
            IdpDataSourceRelation.objects.filter(idp=idp, data_source_id__in=to_delete).delete()

        # 增：现有无，目标有
        if to_create := target_ids - existing_ids:
            IdpDataSourceRelation.objects.bulk_create(
                [
                    IdpDataSourceRelation(
                        idp=idp,
                        data_source_id=ds_id,
                        idp_owner_tenant_id=idp.owner_tenant_id,
                        field_compare_rules=target[ds_id],
                    )
                    for ds_id in to_create
                ]
            )

        # 改：两边都有但规则不同
        for ds_id in existing_ids & target_ids:
            rel = existing[ds_id]
            if rel.field_compare_rules != target[ds_id]:
                rel.field_compare_rules = target[ds_id]
                rel.save(update_fields=["field_compare_rules", "updated_at"])

        IdpDataSourceRelationHandler.sync_local_plugin_config(idp)

    @staticmethod
    def classify_idps_for_deletion(
        owner_tenant_id: str, deleting_ds_ids: Set[int], is_delete_idp: bool
    ) -> IdpDeletionPlan:
        """根据 IDP 与待删除实名数据源的关联情况，决定各 IDP 的处置策略：

        - 删除后仍有其他实名数据源关联：本地 IDP 需同步插件配置，其他类型无需处理
        - 删除后无其他实名数据源关联：用户选了连带删除 or 本地 IDP → 删除，否则 → 禁用
        - 孤儿 IDP（无任何关系记录）：用户选了连带删除时一并清理
        """
        real_idp_ds_map, orphan_idp_ids, idp_map = IdpDataSourceRelationHandler._get_real_idps_with_orphan(
            owner_tenant_id
        )

        plan = IdpDeletionPlan()
        for idp_id, ds_ids in real_idp_ds_map.items():
            ds_id_set = set(ds_ids)
            # 与待删除数据源无关的 IDP，跳过
            if not ds_id_set & deleting_ds_ids:
                continue

            idp = idp_map[idp_id]
            remaining = ds_id_set - deleting_ds_ids
            if remaining:
                # 删除后仍然有其他实名数据源关联，本地 IDP 需同步插件配置
                if idp.is_local:
                    plan.to_sync_local.append(idp)
            # 删除后无其他实名数据源关联，用户选了连带删除 or 本地 IDP → 删除，否则 → 禁用
            elif is_delete_idp or idp.is_local:
                plan.to_delete.append(idp)
            else:
                plan.to_disable.append(idp)

        # 孤儿 IDP（无任何关系记录，通常是之前数据源重置后遗留的）：用户选了连带删除时一并清理
        if is_delete_idp:
            plan.to_delete.extend(idp_map[idp_id] for idp_id in orphan_idp_ids)

        return plan

    @staticmethod
    def _get_real_idps_with_orphan(owner_tenant_id: str) -> Tuple[Dict[str, List[int]], Set[str], Dict[str, Idp]]:
        """获取租户下与实名数据源相关的 IDP，包括有关联关系的和孤儿（无任何关系记录）的。

        返回 (实名数据源关系映射，孤儿 IDP ID 集合，IDP 映射)
        """
        real_idp_ds_map: Dict[str, List[int]] = defaultdict(list)
        all_related_idp_ids: Set[str] = set()

        relations = IdpDataSourceRelation.objects.filter(
            idp_owner_tenant_id=owner_tenant_id,
        ).values("idp_id", "data_source_id", "data_source__type")
        for rel in relations:
            all_related_idp_ids.add(rel["idp_id"])
            if rel["data_source__type"] == DataSourceTypeEnum.REAL:
                real_idp_ds_map[rel["idp_id"]].append(rel["data_source_id"])

        idp_map = {idp.id: idp for idp in Idp.objects.filter(owner_tenant_id=owner_tenant_id)}
        orphan_idp_ids = set(idp_map.keys()) - all_related_idp_ids
        return real_idp_ds_map, orphan_idp_ids, idp_map

    @staticmethod
    @transaction.atomic()
    def set_local_real_relations(idp: Idp, data_sources: List[DataSource]) -> None:
        """为本地登录源建立与同租户指定本地实名数据源的关系，并使用默认匹配规则。

        先清除旧关系再全量重建，适用于初始化或数据源变更后的关系重置场景。
        """
        data_source_ids = [ds.id for ds in data_sources]
        if not data_source_ids:
            return

        IdpDataSourceRelation.objects.filter(idp=idp).delete()
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
