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
from typing import Any, Iterable, List

from django.db import transaction

from bkuser.apps.data_source.constants import DataSourceTypeEnum
from bkuser.apps.data_source.models import DataSource
from bkuser.apps.idp.data_models import (
    DataSourceMatchRule,
    DataSourceMatchRuleList,
    gen_data_source_match_rule_of_local,
)
from bkuser.apps.idp.models import Idp, IdpDataSourceRelation
from bkuser.idp_plugins.constants import BuiltinIdpPluginEnum
from bkuser.idp_plugins.local.plugin import LocalIdpPluginConfig
from bkuser.plugins.constants import DataSourcePluginEnum


class IdpDataSourceRelationHandler:
    """认证源与数据源关系处理器"""

    @staticmethod
    def _dump_field_compare_rules(match_rule: DataSourceMatchRule) -> List[dict[str, Any]]:
        return [r.model_dump() for r in match_rule.field_compare_rules]

    @staticmethod
    def _build_match_rule(relation: IdpDataSourceRelation) -> DataSourceMatchRule:
        return DataSourceMatchRule(
            data_source_id=relation.data_source_id,
            field_compare_rules=relation.field_compare_rules,
        )

    @staticmethod
    def _get_real_data_source_ids(owner_tenant_id: str, plugin_id: str | None = None) -> List[int]:
        queryset = DataSource.objects.filter(owner_tenant_id=owner_tenant_id, type=DataSourceTypeEnum.REAL)
        if plugin_id:
            queryset = queryset.filter(plugin_id=plugin_id)

        return list(queryset.order_by("id").values_list("id", flat=True))

    @classmethod
    def get_relation_data_source_ids(
        cls,
        idp: Idp,
        *,
        data_source_type: str | None = None,
        data_source_plugin_id: str | None = None,
    ) -> List[int]:
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

    @classmethod
    def get_related_real_data_sources(cls, idp: Idp, *, data_source_plugin_id: str | None = None) -> List[DataSource]:
        data_source_ids = cls.get_relation_data_source_ids(
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

    @classmethod
    def get_primary_real_match_rule(cls, idp: Idp) -> DataSourceMatchRule | None:
        real_data_source_ids = cls._get_real_data_source_ids(idp.owner_tenant_id)
        if not real_data_source_ids:
            return None

        relation = (
            IdpDataSourceRelation.objects.filter(idp=idp, data_source_id__in=real_data_source_ids)
            .order_by("created_at", "id")
            .first()
        )
        if relation is None:
            return None

        return cls._build_match_rule(relation)

    @classmethod
    def get_primary_real_data_source(cls, idp: Idp, *, data_source_plugin_id: str | None = None) -> DataSource | None:
        data_sources = cls.get_related_real_data_sources(idp, data_source_plugin_id=data_source_plugin_id)
        return data_sources[0] if data_sources else None

    @classmethod
    def get_real_idp_ids(
        cls, owner_tenant_id: str, *, idp_plugin_id: str | None = None, data_source_plugin_id: str | None = None
    ) -> List[str]:
        data_source_ids = cls._get_real_data_source_ids(owner_tenant_id, plugin_id=data_source_plugin_id)
        if not data_source_ids:
            return []

        idp_ids = list(
            IdpDataSourceRelation.objects.filter(
                idp_owner_tenant_id=owner_tenant_id,
                data_source_id__in=data_source_ids,
            )
            .order_by("idp_id")
            .values_list("idp_id", flat=True)
            .distinct()
        )
        if not idp_ids:
            return []

        queryset = Idp.objects.filter(id__in=idp_ids, owner_tenant_id=owner_tenant_id)
        if idp_plugin_id:
            queryset = queryset.filter(plugin_id=idp_plugin_id)

        return list(queryset.order_by("created_at").values_list("id", flat=True))

    @classmethod
    def get_manageable_idp_ids(cls, owner_tenant_id: str) -> List[str]:
        """获取租户后台登录源列表可见的 IDP。

        关联当前实名数据源的 IDP 可见；数据源被重置但保留登录源时，IDP 会变成无关系的禁用态，
        仍需在后台列表展示，方便管理员后续重新保存配置来建立新关系。
        """
        real_idp_ids = cls.get_real_idp_ids(owner_tenant_id)

        related_idp_ids = list(
            IdpDataSourceRelation.objects.filter(idp_owner_tenant_id=owner_tenant_id)
            .values_list("idp_id", flat=True)
            .distinct()
        )
        orphan_idp_ids = list(
            Idp.objects.filter(owner_tenant_id=owner_tenant_id)
            .exclude(id__in=related_idp_ids)
            .values_list("id", flat=True)
        )

        return list(dict.fromkeys([*real_idp_ids, *orphan_idp_ids]))

    @classmethod
    def has_real_relation(
        cls, idp: Idp, *, data_source_plugin_id: str | None = None, exclude_data_source_id: int | None = None
    ) -> bool:
        data_source_ids = cls._get_real_data_source_ids(idp.owner_tenant_id, plugin_id=data_source_plugin_id)
        if exclude_data_source_id is not None:
            data_source_ids = [
                data_source_id for data_source_id in data_source_ids if data_source_id != exclude_data_source_id
            ]

        return (
            bool(data_source_ids)
            and IdpDataSourceRelation.objects.filter(idp=idp, data_source_id__in=data_source_ids).exists()
        )

    @classmethod
    def has_duplicate_plugin_real_relation(
        cls, owner_tenant_id: str, idp_plugin_id: str, *, exclude_idp_id: str = ""
    ) -> bool:
        idps = Idp.objects.filter(owner_tenant_id=owner_tenant_id, plugin_id=idp_plugin_id)
        if exclude_idp_id:
            idps = idps.exclude(id=exclude_idp_id)

        idp_ids = list(idps.values_list("id", flat=True))
        if not idp_ids:
            return False

        real_data_source_ids = cls._get_real_data_source_ids(owner_tenant_id)
        has_real_relation = (
            bool(real_data_source_ids)
            and IdpDataSourceRelation.objects.filter(
                idp_owner_tenant_id=owner_tenant_id,
                idp_id__in=idp_ids,
                data_source_id__in=real_data_source_ids,
            ).exists()
        )
        if has_real_relation:
            return True

        related_idp_ids = list(
            IdpDataSourceRelation.objects.filter(idp_owner_tenant_id=owner_tenant_id)
            .values_list("idp_id", flat=True)
            .distinct()
        )
        return idps.exclude(id__in=related_idp_ids).exists()

    @classmethod
    def sync_local_plugin_config(cls, idp: Idp) -> None:
        if idp.plugin_id != BuiltinIdpPluginEnum.LOCAL:
            return

        idp.set_plugin_cfg(LocalIdpPluginConfig(data_source_ids=cls.get_relation_data_source_ids(idp)))

    @classmethod
    @transaction.atomic()
    def set_real_relations_from_match_rules(
        cls,
        idp: Idp,
        match_rules: Iterable[dict[str, Any] | DataSourceMatchRule],
    ) -> None:
        """用当前租户下全部实名数据源刷新 IDP 关系。

        当前产品页面仍只配置一个实名数据源的匹配模板，因此这里将提交的首个规则复制到同租户
        全部实名数据源。新增实名数据源后不会自动追加关系，管理员确认数据源 ready 后再次保存
        登录源即可完成覆盖刷新；若未来需要自动追加，推荐在数据源 ready 事件中复用同租户同插件
        已有 IDP 的首个规则生成新关系，并同步本地登录插件配置。
        """
        rules = DataSourceMatchRuleList.validate_python(list(match_rules))
        if not rules:
            return

        real_data_source_ids = cls._get_real_data_source_ids(idp.owner_tenant_id)
        if not real_data_source_ids:
            return

        primary_rule = rules[0]
        rule_map = {rule.data_source_id: cls._dump_field_compare_rules(rule) for rule in rules}
        primary_field_compare_rules = cls._dump_field_compare_rules(primary_rule)

        ordered_data_source_ids = [primary_rule.data_source_id]
        ordered_data_source_ids.extend(
            data_source_id for data_source_id in real_data_source_ids if data_source_id != primary_rule.data_source_id
        )
        ordered_data_source_ids = [
            data_source_id for data_source_id in ordered_data_source_ids if data_source_id in real_data_source_ids
        ]

        IdpDataSourceRelation.objects.filter(idp=idp, data_source_id__in=real_data_source_ids).delete()
        IdpDataSourceRelation.objects.bulk_create(
            [
                IdpDataSourceRelation(
                    idp=idp,
                    data_source_id=data_source_id,
                    idp_owner_tenant_id=idp.owner_tenant_id,
                    field_compare_rules=rule_map.get(data_source_id, primary_field_compare_rules),
                )
                for data_source_id in ordered_data_source_ids
            ]
        )

        cls.sync_local_plugin_config(idp)

    @classmethod
    @transaction.atomic()
    def set_local_real_relations(cls, idp: Idp) -> None:
        data_source_ids = cls._get_real_data_source_ids(idp.owner_tenant_id, plugin_id=DataSourcePluginEnum.LOCAL)
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
        cls.sync_local_plugin_config(idp)

    @classmethod
    @transaction.atomic()
    def set_builtin_management_relation(cls, idp: Idp, data_source: DataSource) -> None:
        IdpDataSourceRelation.objects.filter(idp=idp).delete()
        IdpDataSourceRelation.objects.create(
            idp=idp,
            data_source=data_source,
            idp_owner_tenant_id=idp.owner_tenant_id,
            field_compare_rules=[
                rule.model_dump() for rule in gen_data_source_match_rule_of_local(data_source.id).field_compare_rules
            ],
        )
        cls.sync_local_plugin_config(idp)
