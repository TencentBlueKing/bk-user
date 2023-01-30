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

from typing import TYPE_CHECKING, Dict

from django.conf import settings
from rest_framework import serializers

from bkuser_core.api.web.utils import (
    expand_extra_fields,
    get_category_display_name_map,
    get_extras_with_default_values,
)

if TYPE_CHECKING:
    from bkuser_core.profiles.models import Profile


class SearchInputSLZ(serializers.Serializer):
    keyword = serializers.CharField()
    max_items = serializers.IntegerField(required=False)

    # page = serializers.IntegerField(required=False, default=1)
    # page_size = serializers.IntegerField(required=False, default=10)
    # no_page = serializers.BooleanField(default=False)


class SearchResultProfileLeaderSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    username = serializers.CharField()
    display_name = serializers.CharField(read_only=True)


class SearchResultProfileDepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    category_id = serializers.IntegerField(required=False)


class SearchResultProfileOutputSLZ(serializers.Serializer):
    # NOTE: 搜索结果直接展示列表, 以及点击展示的右侧抽屉表单 => 所以需要全部数据
    id = serializers.IntegerField(required=False)
    username = serializers.CharField(required=True)
    display_name = serializers.CharField(required=True)
    category_id = serializers.IntegerField()
    qq = serializers.CharField(required=False, help_text="QQ")
    email = serializers.CharField(required=False, help_text="邮箱")
    telephone = serializers.CharField(required=False, help_text="电话")
    wx_userid = serializers.CharField(required=False, help_text="微信用户id")
    domain = serializers.CharField(required=False, help_text="域")
    status = serializers.CharField(required=False, help_text="账户状态")
    staff_status = serializers.CharField(required=False, help_text="在职状态")
    position = serializers.CharField(required=False, help_text="职位")
    enabled = serializers.BooleanField(required=False, help_text="是否启用", default=True)
    password_valid_days = serializers.IntegerField(required=False, help_text="密码有效期")
    account_expiration_date = serializers.CharField(required=False)
    country_code = serializers.CharField(required=False, help_text="国家码")
    iso_code = serializers.CharField(required=False, help_text="国家码")
    time_zone = serializers.CharField(required=False, help_text="时区")

    last_login_time = serializers.DateTimeField(required=False, help_text="最后登录时间")
    create_time = serializers.DateTimeField(required=False, help_text="创建时间")
    update_time = serializers.DateTimeField(required=False, help_text="更新时间")

    # extras = serializers.JSONField(required=False, help_text="扩展字段")
    departments = SearchResultProfileDepartmentSerializer(many=True, required=False, help_text="部门列表")
    leader = SearchResultProfileLeaderSerializer(many=True, required=False, help_text="上级列表")

    logo = serializers.SerializerMethodField(required=False)
    extras = serializers.SerializerMethodField(required=False, read_only=True)
    category_name = serializers.SerializerMethodField(required=False)

    # 如果匹配到extras, 则设置这个值用于前端展示
    hit_extra_display_name = serializers.CharField(required=False)

    # NOTE: 这个同 department.profiles 的slz高度一致
    # 目的: 搜索结果或列表结果拿到所有用户数据, 直接展示表单用于编辑 => 所以需要用户全部数据

    def get_logo(self, data):
        logo = data.logo
        if not logo:
            return settings.DEFAULT_LOGO_DATA

        return logo

    def get_category_name(self, obj):
        return get_category_display_name_map().get(obj.category_id, obj.category_id)

    def get_extras(self, obj: "Profile") -> Dict:
        """尝试从 context 中获取默认字段值"""
        return get_extras_with_default_values(obj.extras)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return expand_extra_fields(data)


class SearchResultDepartmentOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    full_name = serializers.CharField()

    category_id = serializers.IntegerField()
    category_name = serializers.SerializerMethodField(required=False)
    enabled = serializers.BooleanField(required=False)

    # order = serializers.IntegerField(required=False)
    # has_children = serializers.SerializerMethodField(required=False)

    # def get_has_children(self, obj) -> bool:
    #     """仅返回启用的子部门"""
    #     # Q: 为什么不用 obj.children.filter(enabled=True).exists()?
    #     # A: 因为 get_descendants 是访问 tree_id 这类的 int 字段，而 children 访问的是 parent 外键字段，前者明显更快
    #     return obj.get_descendants(include_self=False).filter(enabled=True).exists()

    def get_category_name(self, obj):
        return get_category_display_name_map().get(obj.category_id, obj.category_id)


class SearchResultOutputSLZ(serializers.Serializer):
    type = serializers.CharField()
    display_name = serializers.CharField()
    items = serializers.ListField(help_text="Profile 或 Department 对象列表，请直接参考模型定义")
