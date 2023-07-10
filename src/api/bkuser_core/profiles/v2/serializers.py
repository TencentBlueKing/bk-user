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
from typing import Union

from rest_framework import serializers

from bkuser_core.apis.v2.serializers import AdvancedRetrieveSerializer, CustomFieldsMixin, CustomFieldsModelSerializer
from bkuser_core.departments.v2.serializers import ForSyncDepartmentSerializer, SimpleDepartmentSerializer
from bkuser_core.profiles.cache import get_extras_default_from_local_cache
from bkuser_core.profiles.constants import LanguageEnum
from bkuser_core.profiles.models import DynamicFieldInfo, Profile
from bkuser_core.profiles.utils import get_username, parse_username_domain, remove_sensitive_fields_for_profile
from bkuser_core.profiles.validators import validate_domain, validate_username

logger = logging.getLogger(__name__)

# ===============================================================================
# Response
# ===============================================================================


###########
# Profile #
###########


def get_extras(extras_from_db: Union[dict, list]) -> dict:
    extras = {}

    # 1. fill the defaults
    # NOTE: 这里供open api使用, 所以用cache以提升性能
    defaults = get_extras_default_from_local_cache()
    extras.update(defaults)

    # 2. fill the values from db
    formatted_extras = extras_from_db
    # 兼容 1.0 存在的旧数据格式(rubbish)
    # [{"is_deleted":false,"name":"\u804c\u7ea7","is_need":false,"is_import_need":true,"value":"",
    # "is_display":true,"is_editable":true,"is_inner":false,"key":"rank","id":9,"is_only":false,
    # "type":"string","order":9}]
    if isinstance(extras_from_db, list):
        formatted_extras = {x["key"]: x["value"] for x in extras_from_db}

    extras.update(formatted_extras)
    return extras


class LeaderSerializer(CustomFieldsMixin, serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    username = serializers.SerializerMethodField()
    display_name = serializers.CharField(read_only=True)

    def get_username(self, data):
        return get_username(
            data.category_id,
            data.username,
            data.domain,
        )


# TODO: remove this modelSerializer
class ProfileSerializer(CustomFieldsModelSerializer):
    username = serializers.SerializerMethodField()
    password_valid_days = serializers.IntegerField(required=False)

    departments = SimpleDepartmentSerializer(many=True, required=False)
    extras = serializers.SerializerMethodField(required=False)
    leader = LeaderSerializer(many=True, required=False)
    last_login_time = serializers.DateTimeField(required=False, read_only=True)

    def get_extras(self, obj) -> dict:
        """尝试从 context 中获取默认字段值"""
        return get_extras(obj.extras)

    def get_username(self, data):
        return get_username(
            data.category_id,
            data.username,
            data.domain,
        )

    def to_representation(self, obj):
        data = super().to_representation(obj)
        return remove_sensitive_fields_for_profile(self.context.get("request", {}), data)

    class Meta:
        model = Profile
        exclude = ["password"]


class RapidProfileSerializer(CustomFieldsMixin, serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    username = serializers.CharField()
    display_name = serializers.CharField(read_only=True)
    password_valid_days = serializers.IntegerField(required=False)

    # FIXME: 这个slz的full_name也会导致放大查询
    departments = SimpleDepartmentSerializer(many=True, required=False)
    leader = LeaderSerializer(many=True, required=False)

    account_expiration_date = serializers.CharField(required=False)
    create_time = serializers.DateTimeField(required=False, read_only=True)
    update_time = serializers.DateTimeField(required=False, read_only=True)
    extras = serializers.SerializerMethodField(required=False, read_only=True)
    qq = serializers.CharField(read_only=True, allow_blank=True)
    email = serializers.CharField(read_only=True, allow_blank=True)
    telephone = serializers.CharField(read_only=True, allow_blank=True)
    wx_userid = serializers.CharField(read_only=True, allow_blank=True)
    domain = serializers.CharField(read_only=True, allow_blank=True)
    category_id = serializers.IntegerField(read_only=True)
    enabled = serializers.BooleanField(read_only=True)
    iso_code = serializers.CharField(read_only=True)
    country_code = serializers.CharField(read_only=True)
    language = serializers.CharField(read_only=True)
    time_zone = serializers.CharField(read_only=True)
    position = serializers.IntegerField(read_only=True)
    staff_status = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    logo = serializers.CharField(read_only=True, allow_blank=True)

    # 这个字段会导致放大查询, 对外接口不再返回这个字段
    # last_login_time = serializers.DateTimeField(required=False, read_only=True)
    last_login_time = serializers.SerializerMethodField(required=False, read_only=True)

    # NOTE: 这里没有 get_username 的原因是, views中的逻辑处理了

    # NOTE: 禁用掉profiles接口获取last_login_time
    # 影响接口: /api/v2/profiles/ 和 /api/v2/departments/x/profiles/
    def get_last_login_time(self, obj: "Profile"):
        return None

    def get_extras(self, obj: "Profile") -> dict:
        """尝试从 context 中获取默认字段值"""
        return get_extras(obj.extras)

    def to_representation(self, obj):
        data = super().to_representation(obj)
        return remove_sensitive_fields_for_profile(self.context.get("request", {}), data)


class ForSyncRapidProfileSerializer(RapidProfileSerializer):
    """this serializer is for sync data from one bk-user to another
    the api protocol:
    https://github.com/TencentBlueKing/bk-user/blob/development/src/api/bkuser_core/categories/plugins/custom/README.md
    """

    code = serializers.CharField(required=True)
    departments = ForSyncDepartmentSerializer(many=True, required=False)

    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        """change username with domain to raw username
        for sync data between bk-user instances
        """
        return parse_username_domain(obj.username)[0]


class ProfileDepartmentSerializer(AdvancedRetrieveSerializer):
    with_family = serializers.BooleanField(default=False, help_text="是否返回所有祖先（兼容）")
    with_ancestors = serializers.BooleanField(default=False, help_text="是否返回所有祖先")


class ProfileMinimalSerializer(CustomFieldsModelSerializer):
    username = serializers.SerializerMethodField()

    def get_username(self, data):
        return get_username(
            data.category_id,
            data.username,
            data.domain,
        )

    class Meta:
        model = Profile
        fields = ["username", "id"]


##########
# Fields #
##########
class DynamicFieldsSerializer(CustomFieldsModelSerializer):
    name = serializers.CharField()
    options = serializers.JSONField(required=False)
    default = serializers.JSONField(required=False)

    class Meta:
        model = DynamicFieldInfo
        exclude = ("update_time", "create_time")


########
# Edge #
########
class LeaderEdgeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    from_profile_id = serializers.IntegerField()
    to_profile_id = serializers.IntegerField()


# ===============================================================================
# Request
# ===============================================================================

###########
# Profile #
###########
class CreateProfileSerializer(CustomFieldsModelSerializer):
    departments = serializers.ListField(required=False)
    extras = serializers.JSONField(required=False)
    category_id = serializers.IntegerField(required=False)
    domain = serializers.CharField(validators=[validate_domain], required=False)
    username = serializers.CharField(validators=[validate_username])
    position = serializers.IntegerField(required=False)

    class Meta:
        model = Profile
        exclude = ["password"]
        validators: list = []


class UpdateProfileSerializer(CustomFieldsModelSerializer):
    # 批量更新时使用
    id = serializers.IntegerField(required=False)
    departments = serializers.ListField(required=False)
    extras = serializers.JSONField(required=False)

    class Meta:
        model = Profile
        exclude = ["category_id", "username", "domain"]


class UpdateProfileLanguageSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=LanguageEnum.get_choices())
