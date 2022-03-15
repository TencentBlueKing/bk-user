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
from typing import Union

from bkuser_core.apis.v2.serializers import AdvancedRetrieveSerialzier, CustomFieldsMixin, CustomFieldsModelSerializer
from bkuser_core.departments.v2.serializers import SimpleDepartmentSerializer
from bkuser_core.profiles.constants import TIME_ZONE_CHOICES, LanguageEnum, RoleCodeEnum
from bkuser_core.profiles.models import DynamicFieldInfo, Profile
from bkuser_core.profiles.utils import force_use_raw_username, get_username
from bkuser_core.profiles.validators import validate_domain, validate_username
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import ValidationError

# ===============================================================================
# Response
# ===============================================================================


###########
# Profile #
###########


def get_extras(extras_from_db: Union[dict, list], defaults: dict) -> dict:

    if not defaults:
        defaults = DynamicFieldInfo.objects.get_extras_default_values()

    formatted_extras = extras_from_db

    # 兼容 1.0 存在的旧数据格式(rubbish)
    # [{"is_deleted":false,"name":"\u804c\u7ea7","is_need":false,"is_import_need":true,"value":"",
    # "is_display":true,"is_editable":true,"is_inner":false,"key":"rank","id":9,"is_only":false,
    # "type":"string","order":9}]
    if isinstance(extras_from_db, list):
        formatted_extras = {x["key"]: x["value"] for x in extras_from_db}

    defaults.update(formatted_extras)
    return defaults


class LeaderSerializer(CustomFieldsMixin, serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    username = serializers.SerializerMethodField()
    display_name = serializers.CharField(read_only=True)

    def get_username(self, data):
        return get_username(
            force_use_raw_username(self.context.get("request")),
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
        return get_extras(obj.extras, self.context.get("extra_defaults", {}).copy())

    def get_username(self, data):
        return get_username(
            force_use_raw_username(self.context.get("request")),
            data.category_id,
            data.username,
            data.domain,
        )

    class Meta:
        model = Profile
        exclude = ["password"]


class RapidProfileSerializer(CustomFieldsMixin, serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    username = serializers.CharField()
    display_name = serializers.CharField(read_only=True)
    password_valid_days = serializers.IntegerField(required=False)

    departments = SimpleDepartmentSerializer(many=True, required=False)
    leader = LeaderSerializer(many=True, required=False)
    last_login_time = serializers.DateTimeField(required=False, read_only=True)

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

    def get_extras(self, obj: "Profile") -> dict:
        """尝试从 context 中获取默认字段值"""
        return get_extras(obj.extras, self.context.get("extra_defaults", {}).copy())


class ProfileDepartmentSerializer(AdvancedRetrieveSerialzier):
    with_family = serializers.BooleanField(default=False, help_text="是否返回所有祖先（兼容）")
    with_ancestors = serializers.BooleanField(default=False, help_text="是否返回所有祖先")


class ProfileMinimalSerializer(CustomFieldsModelSerializer):
    username = serializers.SerializerMethodField()

    def get_username(self, data):
        return get_username(
            force_use_raw_username(self.context.get("request")),
            data.category_id,
            data.username,
            data.domain,
        )

    class Meta:
        model = Profile
        fields = ["username", "id"]


#########
# Login #
#########
class LoginBatchResponseSerializer(serializers.Serializer):
    username = serializers.SerializerMethodField()
    chname = serializers.CharField(source="display_name")
    display_name = serializers.CharField()
    qq = serializers.CharField()
    phone = serializers.CharField(source="telephone")
    wx_userid = serializers.CharField()
    language = serializers.CharField()
    time_zone = serializers.CharField()
    email = serializers.CharField()
    role = serializers.IntegerField()

    def get_username(self, data):
        return get_username(
            force_use_raw_username(self.context.get("request")),
            data.category_id,
            data.username,
            data.domain,
        )


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


class ProfileFieldsSerializer(DynamicFieldsSerializer):
    value = serializers.CharField()

    class Meta:
        model = DynamicFieldInfo
        exclude = ("update_time", "create_time")


#########
# Token #
#########
class ProfileTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


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


##########
# Fields #
##########
class CreateFieldsSerializer(DynamicFieldsSerializer):
    def validate(self, attrs):
        if DynamicFieldInfo.objects.filter(name=attrs["name"]).exists():
            raise ValidationError(_("英文标识为 {} 的自定义字段已存在").format(attrs["name"]))

        return super().validate(attrs)


#########
# Login #
#########
class ProfileLoginSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="用户名")
    password = serializers.CharField(help_text="用户密码")
    domain = serializers.CharField(required=False, help_text="用户所属目录 domain，当登录用户不属于默认目录时必填")


class LoginUpsertSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, min_length=1, max_length=255)
    display_name = serializers.CharField(required=False, min_length=1, max_length=255, allow_blank=True)
    domain = serializers.CharField(required=False, validators=[validate_domain])

    qq = serializers.CharField(required=False, min_length=5, max_length=64, allow_blank=True)
    telephone = serializers.CharField(required=False, min_length=11, max_length=11)
    email = serializers.EmailField(required=False)
    role = serializers.ChoiceField(required=False, choices=RoleCodeEnum.get_choices())
    position = serializers.CharField(required=False)
    language = serializers.ChoiceField(required=False, choices=LanguageEnum.get_choices())
    time_zone = serializers.ChoiceField(required=False, choices=TIME_ZONE_CHOICES)
    status = serializers.CharField(required=False)
    staff_status = serializers.CharField(required=False)
    wx_userid = serializers.CharField(required=False, allow_blank=True)


class LoginBatchQuerySerializer(serializers.Serializer):
    username_list = serializers.ListField(child=serializers.CharField(), required=False)
    is_complete = serializers.BooleanField(required=False)


############
# Password #
############
class ProfileModifyPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, max_length=254)
    new_password = serializers.CharField(required=True, max_length=254)
