# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import re
from typing import Any, Dict, List

import pydantic
from django.conf import settings

from bkuser.apps.data_source.constants import FieldMappingOperation
from bkuser.apps.data_source.data_models import DataSourceUserFieldMapping
from bkuser.apps.data_source.models import DataSource, DataSourceUser
from bkuser.apps.sync.constants import DATA_SOURCE_USERNAME_REGEX, EMAIL_REGEX
from bkuser.apps.sync.context import TaskLogger
from bkuser.apps.tenant.constants import UserFieldDataType
from bkuser.apps.tenant.models import TenantUserCustomField, UserBuiltinField
from bkuser.common.validators import validate_phone_with_country_code
from bkuser.plugins.models import RawDataSourceUser
from bkuser.utils.pydantic import stringify_pydantic_error


class DataSourceUserConverter:
    """数据源用户转换器"""

    def __init__(self, data_source: DataSource, logger: TaskLogger):
        self.data_source = data_source
        self.logger = logger
        self.custom_fields = TenantUserCustomField.objects.filter(tenant_id=self.data_source.owner_tenant_id)
        self.field_mapping = self._get_field_mapping()

    def convert(self, user: RawDataSourceUser) -> DataSourceUser:
        # TODO (su) 支持复杂字段映射类型，如表达式，目前都当作直接映射处理（目前只支持直接映射）
        mapping = {m.target_field: m.source_field for m in self.field_mapping}
        props = user.properties

        username = props.get(mapping["username"])
        # 1. 用户名是必须提供的，而且需要满足正则校验规则
        if not username:
            raise ValueError("username is required")

        if not re.fullmatch(DATA_SOURCE_USERNAME_REGEX, username):
            raise ValueError(f"username [{username}] not match pattern {DATA_SOURCE_USERNAME_REGEX.pattern}")

        # 2. 姓名也是必须提供的
        full_name = props.get(mapping["full_name"])
        if not full_name:
            raise ValueError(f"username {username}, full_name is required")

        email = props.get(mapping.get("email")) or ""  # type: ignore
        # 3. 如果提供了邮箱，则必须满足正则校验规则
        if email and not re.fullmatch(EMAIL_REGEX, email):
            raise ValueError(
                f"username {username}, email [{email}] provided but not match pattern {EMAIL_REGEX.pattern}"
            )

        phone = props.get(mapping.get("phone")) or ""  # type: ignore
        country_code = (
            props.get(
                mapping.get("phone_country_code"),  # type: ignore
            )
            or settings.DEFAULT_PHONE_COUNTRY_CODE
        )
        # 4. 如果提供了手机号，则需要通过 phonenumbers 的检查，确保手机号码合法
        if phone:
            validate_phone_with_country_code(phone, country_code)

        return DataSourceUser(
            data_source=self.data_source,
            code=user.code,
            username=username,
            full_name=full_name,
            email=email,
            phone=phone,
            phone_country_code=country_code,
            extras=self._build_extras(username, props, mapping),
        )

    def _get_field_mapping(self) -> List[DataSourceUserFieldMapping]:
        """获取字段映射配置"""
        if self.data_source.is_local:
            self.logger.info("local data source field mapping can only generated from field settings")
            field_mapping = self._get_field_mapping_from_tenant_user_fields()
        else:
            # 1. 尝试从数据源配置中获取
            field_mapping = self._get_field_mapping_from_data_source_config()
            if not field_mapping:
                self.logger.warning(
                    f"data source (id: {self.data_source.id}) hasn't field mapping,"  # noqa: G004
                    "generated from field settings...",
                )
                # 2. 若数据源配置中不存在，或者格式异常，则根据字段配置中生成，字段映射方式为直接映射
                field_mapping = self._get_field_mapping_from_tenant_user_fields()

        self.logger.info(
            f"use {[str(m) for m in field_mapping]} as data source (id: {self.data_source.id}) field mapping"  # noqa: G004, E501
        )
        return field_mapping

    def _get_field_mapping_from_data_source_config(self) -> List[DataSourceUserFieldMapping]:
        """根据 data_source.field_mapping 获取字段映射配置"""
        try:
            return [DataSourceUserFieldMapping(**mapping) for mapping in self.data_source.field_mapping]
        except pydantic.ValidationError as e:
            self.logger.warning(
                f"data source (id: {self.data_source.id}) has invalid field mapping: "  # noqa: G004
                f"{self.data_source.field_mapping}, error: {stringify_pydantic_error(e)}"
            )

        return []

    def _get_field_mapping_from_tenant_user_fields(self) -> List[DataSourceUserFieldMapping]:
        """根据内置用户字段 + 租户用户自定义字段，生成字段映射配置"""
        return [
            DataSourceUserFieldMapping(
                source_field=f.name,
                mapping_operation=FieldMappingOperation.DIRECT,
                target_field=f.name,
            )
            for fields in [UserBuiltinField.objects.all(), self.custom_fields]
            for f in fields
        ]

    def _build_extras(self, username: str, props: Dict[str, str], mapping: Dict[str, str]) -> Dict[str, Any]:  # noqa: C901
        extras = {}
        for f in self.custom_fields:
            # 并不是所有的自定义字段，都已经被配置到字段映射中，这里应该以字段映射为准
            if f.name not in mapping:
                continue

            opt_ids = [opt["id"] for opt in f.options]
            value = props.get(mapping[f.name], f.default)

            # 数字类型，转换成整型不丢精度就转，不行就浮点数
            if f.data_type == UserFieldDataType.NUMBER:
                try:
                    value = float(value)  # type: ignore
                    value = int(value) if int(value) == value else value  # type: ignore
                except ValueError:
                    raise ValueError(
                        f"username: {username}, number field {f.name} value `{value}` cannot convert to number"
                    )
            # 枚举类型，值（id）必须是字符串，且是可选项中的一个
            elif f.data_type == UserFieldDataType.ENUM:
                if value not in opt_ids:
                    raise ValueError(
                        f"username: {username}, enum field {f.name} value `{value}` not in options {opt_ids}"
                    )
            # 多选枚举类型，值必须是字符串列表，且是可选项的子集
            elif f.data_type == UserFieldDataType.MULTI_ENUM:
                # 兼容 xlsx 导入，统一所有插件输出的多选枚举，都是通过 "," 分隔的字符串表示列表
                # 但是，默认值 default 可能是 list 类型，因此这里还是需要做类型判断的
                if isinstance(value, str):
                    value = [v.strip() for v in value.split(",") if v.strip()]  # type: ignore

                if set(value) - set(opt_ids):
                    raise ValueError(
                        f"username: {username}, multi enum field {f.name} value `{value}` not subset of {opt_ids}"
                    )
            # 必填字段检查仅适用于字符串类型字段，因为数字类型即使是 0 也不能判断是空，枚举类型都有值检查
            elif f.data_type == UserFieldDataType.STRING and f.required and not value:
                raise ValueError(f"username: {username}, field {f.name} is required")

            extras[f.name] = value

        return extras
