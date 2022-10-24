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

from django.utils.translation import ugettext as _
from rest_framework import serializers

from bkuser_core.apis.serializers import StringArrayField


class CustomFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        user_fields = kwargs.pop("fields", None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if user_fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(user_fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class CustomFieldsMixin:
    """
    A Serializer that takes an additional `fields` argument that
    controls which fields should be displayed.

    Universal mixin
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        user_fields = kwargs.pop("fields", None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if user_fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(user_fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


def is_custom_fields_enabled(slz: serializers.Serializer) -> bool:
    """判断当前 Serializer 是否支持动态返回字段"""
    if isinstance(slz, CustomFieldsModelSerializer):
        return True

    if issubclass(slz.__class__, CustomFieldsMixin):
        return True
    return False


class AdvancedListSerializer(serializers.Serializer):
    fields = StringArrayField(required=False, help_text=_("指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id"))
    lookup_field = serializers.CharField(required=False, help_text=_("查询字段，针对 exact_lookups,fuzzy_lookups 生效"))
    exact_lookups = StringArrayField(
        required=False,
        help_text=_("精确查询 lookup_field 所指定的字段, 支持多选，以逗号分隔，例如: cat,dog,fish"),
    )
    fuzzy_lookups = StringArrayField(
        required=False,
        help_text=_("模糊查询 lookup_field 所指定的字段, 支持多选，以逗号分隔，例如: cat,dog,fish"),
    )
    wildcard_search = serializers.CharField(required=False, help_text=_("在多个字段模糊搜索的内容"))
    wildcard_search_fields = StringArrayField(required=False, help_text=_("指定多个模糊搜索字段"))
    best_match = serializers.BooleanField(required=False, default=False, help_text=_("是否按照最短匹配排序"))
    time_field = serializers.ChoiceField(
        required=False,
        default="create_time",
        choices=["update_time", "create_time"],
        help_text=_("时间过滤字段，支持 update_time, create_time"),
    )
    since = serializers.DateTimeField(
        required=False,
        input_formats=["iso-8601", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S"],
        help_text=_("筛选某个时间点后的记录"),
    )
    until = serializers.DateTimeField(
        required=False,
        input_formats=["iso-8601", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S"],
        help_text=_("筛选某个时间点前的记录"),
    )
    include_disabled = serializers.BooleanField(required=False, default=False, help_text=_("是否包含已软删除的数据"))


class AdvancedRetrieveSerializer(serializers.Serializer):
    fields = serializers.CharField(required=False, help_text=_("指定对象返回字段，支持多选，以逗号分隔，例如: username,status,id"))
    lookup_field = serializers.CharField(required=False, help_text=_("指定查询字段，内容为 lookup_value 所属字段, 例如: username"))
    include_disabled = serializers.BooleanField(required=False, default=False, help_text=_("是否包含已软删除的数据"))


class EmptySerializer(serializers.Serializer):
    """空"""
