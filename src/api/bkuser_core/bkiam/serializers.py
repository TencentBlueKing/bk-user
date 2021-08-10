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
from rest_framework.fields import empty
from rest_framework.serializers import (
    CharField,
    ChoiceField,
    IntegerField,
    JSONField,
    ListField,
    Serializer,
    SerializerMethodField,
)

from .constants import IAMCallbackMethods


# -------------- Common --------------
class IAMPageSerializer(Serializer):
    offset = IntegerField(required=False)
    limit = IntegerField(required=False)


class IAMPageResponseSerializer(Serializer):
    page = IAMPageSerializer(required=False)


class IAMMethodSerializer(Serializer):
    """IAM Method Serializer"""

    type = CharField()
    method = ChoiceField(choices=IAMCallbackMethods.get_choices())
    filter = JSONField(required=False)
    page = IAMPageSerializer(required=False)


class RelatedResourceSLZ(Serializer):
    id = CharField(read_only=True)
    name = CharField(read_only=True)
    type = CharField(read_only=True)
    type_name = CharField(read_only=True)


class AuthInfoSLZ(Serializer):
    id = CharField(read_only=True)
    display_name = CharField(read_only=True)
    related_resources = ListField(read_only=True, child=RelatedResourceSLZ())


############
# Response #
############
class IAMInstanceRespSLZ(Serializer):
    """IAM Common Response"""

    def __init__(self, instance=None, data=empty, id_display_name_pair=("id", "display_name"), **kwargs):
        super().__init__(instance=None, data=empty, **kwargs)

        self.id_display_name_pair = id_display_name_pair

    id = SerializerMethodField(read_only=True)
    display_name = SerializerMethodField(read_only=True)

    def get_id(self, obj) -> str:
        return str(getattr(obj, self.id_display_name_pair[0]))

    def get_display_name(self, obj) -> str:
        return str(getattr(obj, self.id_display_name_pair[1]))


class DepartmentInstanceRespSLZ(IAMInstanceRespSLZ):
    child_type = SerializerMethodField(read_only=True)

    def get_child_type(self, obj) -> str:
        if obj.children.filter(enabled=True).exists():
            return "department"
        else:
            return ""


# -------------- List Attr Value --------------
class IAMListAttrValueFilterSLZ(Serializer):
    attr = CharField()
    keyword = CharField(required=False)
    ids = ListField(required=False, child=CharField())


class IAMListAttrValueSLZ(IAMMethodSerializer):
    filter = IAMListAttrValueFilterSLZ(required=False)


# -------------- List Instances --------------
class IAMInstancesParentSLZ(Serializer):
    type = CharField()
    id = CharField()


class IAMInstanceParentSLZ(Serializer):
    id = CharField()
    type = CharField()


class IAMInstancesFilterSLZ(Serializer):
    parent = IAMInstanceParentSLZ(required=False)
    keyword = CharField(required=False)


class IAMListInstancesSLZ(IAMMethodSerializer):
    filter = IAMInstancesFilterSLZ(required=False)


# -------------- Fetch Instance Info --------------
class IAMFetchInstanceInfoFilterSLZ(Serializer):
    attrs = ListField(required=False)
    ids = ListField(child=CharField())


class IAMFetchInstanceInfoSLZ(IAMMethodSerializer):
    filter = IAMFetchInstanceInfoFilterSLZ(required=False)


# -------------- List Instance By Policy --------------
class IAMInstancePolicyFilterSLZ(IAMMethodSerializer):
    expression = JSONField(required=False)


class IAMInstancePolicySLZ(IAMMethodSerializer):
    filter = IAMInstancePolicyFilterSLZ(required=False)
