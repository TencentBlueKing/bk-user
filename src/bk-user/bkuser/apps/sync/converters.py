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
from typing import List

from django.conf import settings
from pydantic import ValidationError

from bkuser.apps.data_source.constants import FieldMappingOperation
from bkuser.apps.data_source.data_models import DataSourceUserFieldMapping
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.tenant.models import TenantUserCustomField, UserBuiltinField
from bkuser.plugins.models import RawDataSourceUser

logger = logging.getLogger(__name__)


class DataSourceUserConverter:
    """数据源用户转换器"""

    def __init__(self, data_source: DataSource):
        self.data_source = data_source
        self.custom_fields = TenantUserCustomField.objects.filter(tenant_id=self.data_source.owner_tenant_id)
        self.field_mapping = self._get_field_mapping()

    def _get_field_mapping(self) -> List[DataSourceUserFieldMapping]:
        """获取字段映射配置"""
        # 1. 尝试从数据源配置中获取
        field_mapping = []
        try:
            field_mapping = [DataSourceUserFieldMapping(**mapping) for mapping in self.data_source.field_mapping]
        except ValidationError as e:
            logger.warning("data source (id: %s) has invalid field mapping: %s", self.data_source.id, e)

        if field_mapping:
            return field_mapping

        # 2. 若数据源配置中不存在，或者格式异常，则根据字段配置中生成，字段映射方式为直接映射
        logger.warning("data source (id: %s) has no field mapping, generate from field settings", self.data_source.id)

        for fields in [UserBuiltinField.objects.all(), self.custom_fields]:
            for f in fields:
                field_mapping.append(  # noqa: PERF401
                    DataSourceUserFieldMapping(
                        source_field=f.name,
                        mapping_operation=FieldMappingOperation.DIRECT,
                        target_field=f.name,
                    )
                )

        return field_mapping

    def convert(self, user: RawDataSourceUser) -> DataSourceUser:
        # TODO (su) 重构，支持复杂字段映射类型，如表达式，目前都当作直接映射处理（本地数据源只有直接映射）
        mapping = {m.source_field: m.target_field for m in self.field_mapping}
        props = user.properties
        return DataSourceUser(
            data_source=self.data_source,
            code=user.code,
            username=props[mapping["username"]],
            full_name=props[mapping["full_name"]],
            email=props[mapping["email"]],
            phone=props[mapping["phone"]],
            phone_country_code=props.get(mapping["phone_country_code"], settings.DEFAULT_PHONE_COUNTRY_CODE),
            extras={f.name: props.get(f.name, f.default) for f in self.custom_fields},
        )
