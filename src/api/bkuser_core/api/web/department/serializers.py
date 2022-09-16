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

from rest_framework import serializers

from bkuser_core.departments.models import Department


class RapidDepartmentSerializer(serializers.Serializer):
    """极简返回"""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class DepartmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    has_children = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    order = serializers.IntegerField(required=False)
    extras = serializers.JSONField(required=False)
    enabled = serializers.BooleanField(default=True, required=False)

    def get_full_name(self, obj):
        return obj.full_name

    def get_has_children(self, obj) -> bool:
        """仅返回启用的子部门"""
        # Q: 为什么不用 obj.children.filter(enabled=True).exists()?
        # A: 因为 get_descendants 是访问 tree_id 这类的 int 字段，而 children 访问的是 parent 外键字段，前者明显更快
        return obj.get_descendants(include_self=False).filter(enabled=True).exists()

    class Meta:
        # ref_name = "v2_department"
        model = Department
        exclude = ("profiles", "update_time", "create_time", "lft", "rght", "tree_id", "level", "parent", "code")


class DepartmentWithChildrenSLZ(DepartmentSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj) -> List[Dict]:
        """不使用 serializer 而是手动取数据，避免重复查询 DB"""
        full_name_prefix = obj.full_name

        items = {}
        all_children = obj.children.filter(enabled=True)
        for x in all_children:
            # children 可能存在重复
            if x.pk in items:
                continue

            full_name = f"{full_name_prefix}/{x.name}"
            # 由于当前删除是假删除，真实架构树并未移除 has_children = not x.is_leaf_node()
            has_children = x.get_children().filter(enabled=True).exists()
            y = {"id": x.pk, "name": x.name, "full_name": full_name, "has_children": has_children}
            items.update({x.pk: y})

        return list(items.values())


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
    extras = serializers.JSONField(required=False, help_text="扩展字段")
    password_valid_days = serializers.IntegerField(required=False, help_text="密码有效期")
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
