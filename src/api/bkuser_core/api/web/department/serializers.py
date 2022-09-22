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
from typing import TYPE_CHECKING, Dict, List

from django.conf import settings
from rest_framework import serializers

from bkuser_core.departments.models import Department
from bkuser_core.profiles.cache import get_extras_default_from_local_cache
from bkuser_core.profiles.v2.serializers import get_extras

if TYPE_CHECKING:
    from bkuser_core.profiles.models import Profile


class RapidDepartmentSerializer(serializers.Serializer):
    """极简返回"""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class DepartmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    order = serializers.IntegerField(required=False)
    extras = serializers.JSONField(required=False)
    enabled = serializers.BooleanField(default=True, required=False)

    full_name = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return obj.full_name

    def get_has_children(self, obj) -> bool:
        return obj.has_children

    class Meta:
        model = Department
        exclude = ("profiles", "update_time", "create_time", "lft", "rght", "tree_id", "level", "parent", "code")


class DepartmentWithChildrenSLZ(DepartmentSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj) -> List[Dict]:
        """不使用 serializer 而是手动取数据，避免重复查询 DB"""
        full_name_prefix = obj.full_name

        data = []
        items = {}
        all_children = obj.children.filter(enabled=True)
        for x in all_children:
            # children 可能存在重复
            if x.pk in items:
                continue
            items[x.pk] = True

            full_name = f"{full_name_prefix}/{x.name}"
            # 由于当前删除是假删除，真实架构树并未移除 has_children = not x.is_leaf_node()
            has_children = x.get_children().filter(enabled=True).exists()
            y = {"id": x.pk, "name": x.name, "full_name": full_name, "has_children": has_children, "order": x.order}
            data.append(y)

        # sort by order asc
        data.sort(key=lambda x: x["order"])
        return data


class DepartmentsWithChildrenAndAncestorsOutputSLZ(DepartmentWithChildrenSLZ):
    ancestors = serializers.SerializerMethodField()

    def get_ancestors(self, instance) -> List:
        family = instance.get_ancestors()
        return RapidDepartmentSerializer(family, many=True).data


class DepartmentCreatedOutputSLZ(DepartmentSerializer):
    class Meta:
        # ref_name = "v2_department"
        model = Department
        fields = ("id", "name", "order", "enabled", "full_name", "has_children", "category_id")


class DepartmentCreateInputSLZ(serializers.Serializer):
    name = serializers.CharField()
    parent = serializers.IntegerField(required=False)
    category_id = serializers.IntegerField()


# class DepartmentUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Department
#         fields = ("name",)


class DepartmentSearchInputSLZ(serializers.Serializer):
    category_id = serializers.IntegerField()


class DepartmentSearchOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    category_id = serializers.IntegerField(required=False)


class DepartmentProfileListInputSLZ(serializers.Serializer):
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=10)
    recursive = serializers.BooleanField(default=True)
    keyword = serializers.CharField(required=False)


class DepartmentProfilesCreateInputSLZ(serializers.Serializer):
    profile_id_list = serializers.ListField(child=serializers.IntegerField())


class DepartmentProfileLeaderSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    username = serializers.CharField()
    display_name = serializers.CharField(read_only=True)


class DepartmentProfileDepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    category_id = serializers.IntegerField(required=False)


class DepartmentProfileOutputSLZ(serializers.Serializer):
    # FIXME: 不需要返回所有字段吧
    id = serializers.CharField(required=False, help_text="用户ID")
    username = serializers.CharField(required=False, help_text="用户名")
    qq = serializers.CharField(required=False, help_text="QQ")
    email = serializers.CharField(required=False, help_text="邮箱")
    telephone = serializers.CharField(required=False, help_text="电话")
    wx_userid = serializers.CharField(required=False, help_text="微信用户id")
    domain = serializers.CharField(required=False, help_text="域")
    display_name = serializers.CharField(required=False, help_text="中文名")
    status = serializers.CharField(required=False, help_text="账户状态")
    staff_status = serializers.CharField(required=False, help_text="在职状态")
    position = serializers.CharField(required=False, help_text="职位")
    enabled = serializers.BooleanField(required=False, help_text="是否启用", default=True)
    # extras = serializers.JSONField(required=False, help_text="扩展字段")
    password_valid_days = serializers.IntegerField(required=False, help_text="密码有效期")
    account_expiration_date = serializers.CharField(required=False)
    country_code = serializers.CharField(required=False, help_text="国家码")
    iso_code = serializers.CharField(required=False, help_text="国家码")
    time_zone = serializers.CharField(required=False, help_text="时区")

    last_login_time = serializers.DateTimeField(required=False, help_text="最后登录时间")

    create_time = serializers.DateTimeField(required=False, help_text="创建时间")
    update_time = serializers.DateTimeField(required=False, help_text="更新时间")
    departments = DepartmentProfileDepartmentSerializer(many=True, required=False, help_text="部门列表")

    # FIXME: 老的代码用的leader, 需要切换成leaders
    # leaders = DepartmentProfileLeaderSerializer(many=True, required=False, help_text="上级列表", source="leader")
    leader = DepartmentProfileLeaderSerializer(many=True, required=False, help_text="上级列表")

    logo = serializers.SerializerMethodField(required=False)
    extras = serializers.SerializerMethodField(required=False, read_only=True)

    def get_extras(self, obj: "Profile") -> dict:
        """尝试从 context 中获取默认字段值"""
        extra_defaults = self.context.get("extra_defaults", {}).copy()
        return get_extras(obj.extras, extra_defaults)

    def get_logo(self, data):
        logo = data.logo
        if not logo:
            # logo转成 "data:image/png;base64,xxxxx"
            return settings.DEFAULT_LOGO_DATA

        return logo

    # NOTE: 部门下的用户列表需要把字段extras打平到profile的字段(用于页面展示+修改表单直接编辑/提交)
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return expand_extra_fields(self.context.get("fields"), data)


def expand_extra_fields(extra_fields, profile):
    """将 profile extra value 展开，作为 profile 字段展示"""
    available_values = profile.pop("extras")

    extras_default = get_extras_default_from_local_cache()
    # TODO: 建模, 建模, 建模
    for key, default in extras_default.items():
        # 没有设置额外字段，则使用字段默认值
        profile[key] = default
        if not available_values:
            continue

        # 兼容旧的数据格式
        if isinstance(available_values, list):
            available_values = {x["key"]: x["value"] for x in available_values}

        profile[key] = available_values.get(key)

    return profile
