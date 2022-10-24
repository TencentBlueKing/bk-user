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
from rest_framework import serializers
from rest_framework.fields import empty

from .constants import IAMCallbackMethods


# -------------- Common --------------
class IAMPageSerializer(serializers.Serializer):
    offset = serializers.IntegerField(required=False)
    limit = serializers.IntegerField(required=False)


class IAMPageResponseSerializer(serializers.Serializer):
    page = IAMPageSerializer(required=False)


class IAMMethodSerializer(serializers.Serializer):
    """IAM Method Serializer"""

    type = serializers.CharField()
    method = serializers.ChoiceField(choices=IAMCallbackMethods.get_choices())
    filter = serializers.JSONField(required=False)
    page = IAMPageSerializer(required=False)


class RelatedResourceSLZ(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    type = serializers.CharField(read_only=True)
    type_name = serializers.CharField(read_only=True)


class AuthInfoSLZ(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    related_resources = serializers.ListField(read_only=True, child=RelatedResourceSLZ())


############
# Response #
############
class IAMInstanceRespSLZ(serializers.Serializer):
    """IAM Common Response"""

    def __init__(self, instance=None, data=empty, id_display_name_pair=("id", "display_name"), **kwargs):
        super().__init__(instance=None, data=empty, **kwargs)

        self.id_display_name_pair = id_display_name_pair

    id = serializers.SerializerMethodField(read_only=True)
    display_name = serializers.SerializerMethodField(read_only=True)

    def get_id(self, obj) -> str:
        return str(getattr(obj, self.id_display_name_pair[0]))

    def get_display_name(self, obj) -> str:
        return str(getattr(obj, self.id_display_name_pair[1]))


class DepartmentInstanceRespSLZ(IAMInstanceRespSLZ):
    child_type = serializers.SerializerMethodField(read_only=True)

    def get_child_type(self, obj) -> str:
        if obj.children.filter(enabled=True).exists():
            return "department"
        else:
            return ""


# -------------- List Attr Value --------------
class IAMListAttrValueFilterSLZ(serializers.Serializer):
    attr = serializers.CharField()
    keyword = serializers.CharField(required=False)
    ids = serializers.ListField(required=False, child=serializers.CharField())


class IAMListAttrValueSLZ(IAMMethodSerializer):
    filter = IAMListAttrValueFilterSLZ(required=False)


# -------------- List Instances --------------
class IAMInstancesParentSLZ(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.CharField()


class IAMInstanceParentSLZ(serializers.Serializer):
    id = serializers.CharField()
    type = serializers.CharField()


class IAMInstancesFilterSLZ(serializers.Serializer):
    parent = IAMInstanceParentSLZ(required=False)
    keyword = serializers.CharField(required=False)


class IAMListInstancesSLZ(IAMMethodSerializer):
    filter = IAMInstancesFilterSLZ(required=False)


# -------------- Fetch Instance Info --------------
class IAMFetchInstanceInfoFilterSLZ(serializers.Serializer):
    attrs = serializers.ListField(required=False)
    ids = serializers.ListField(child=serializers.CharField())


class IAMFetchInstanceInfoSLZ(IAMMethodSerializer):
    filter = IAMFetchInstanceInfoFilterSLZ(required=False)


# -------------- List Instance By Policy --------------
class IAMInstancePolicyFilterSLZ(IAMMethodSerializer):
    expression = serializers.JSONField(required=False)


class IAMInstancePolicySLZ(IAMMethodSerializer):
    filter = IAMInstancePolicyFilterSLZ(required=False)
