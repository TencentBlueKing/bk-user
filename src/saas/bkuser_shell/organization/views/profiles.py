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

import bkuser_sdk
from bkuser_shell.bkiam.constants import ActionEnum
from bkuser_shell.common.error_codes import error_codes
from bkuser_shell.common.response import Response
from bkuser_shell.common.viewset import BkUserApiViewSet
from bkuser_shell.organization.serializers import profiles as serializers
from bkuser_shell.organization.utils import expand_extra_fields, get_default_logo_url
from rest_framework.permissions import IsAuthenticated

from bkuser_global.drf_crown import ResponseParams, inject_serializer

logger = logging.getLogger(__name__)


class LoginInfoViewSet(BkUserApiViewSet):

    permission_classes = [
        IsAuthenticated,
    ]

    @inject_serializer(out=serializers.LoginInfoSerializer, tags=["profiles"])
    def me(self, request):
        api_instance = bkuser_sdk.ProfilesApi(self.get_api_client_by_request(request))
        try:
            profile = api_instance.v2_profiles_read(request.user.username)
        except Exception:  # pylint: disable=broad-except
            logger.exception(
                "Exception when calling ProfilesApi->profiles_read<%s> \n",
                request.user.username,
            )
            # 兼容测试环境
            profile = {
                "username": request.user.username,
                "logo": get_default_logo_url(request),
            }

        return ResponseParams(profile, {"context": {"request": request}})


class ProfilesViewSet(BkUserApiViewSet):

    permission_classes = [IsAuthenticated]
    ACTION_ID = ActionEnum.MANAGE_DEPARTMENT.value

    @inject_serializer(
        body_in=serializers.CreateProfileSerializer, out=serializers.ProfileSerializer, tags=["profiles"]
    )
    def create(self, request, validated_data):
        api_instance = bkuser_sdk.CategoriesApi(self.get_api_client_by_request(request, no_auth=True))
        category = api_instance.v2_categories_read(validated_data["category_id"])

        api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request, no_auth=True))
        fields = self.get_paging_results(api_instance.v2_dynamic_fields_list)

        extra_fields = {key: value for key, value in request.data.items() if key not in validated_data}
        unknown_fields = set(extra_fields.keys()) - set([x["name"] for x in fields if not x["builtin"]])  # noqa
        if unknown_fields:
            raise error_codes.UNKNOWN_FIELD.f(", ".join(list(unknown_fields)))

        validated_data["extras"] = {key: value for key, value in extra_fields.items()}

        # 保证 category_id 和 domain 一一对应
        domain = category.domain
        validated_data["domain"] = domain
        profile = bkuser_sdk.Profile(**validated_data)
        api_instance = bkuser_sdk.ProfilesApi(self.get_api_client_by_request(request))
        return api_instance.v2_profiles_create(body=profile)

    @inject_serializer(
        body_in=serializers.UpdateProfileSerializer, out=serializers.ProfileSerializer, tags=["profiles"]
    )
    def update(self, request, profile_id, validated_data):
        api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request, no_auth=True))
        fields = self.get_paging_results(api_instance.v2_dynamic_fields_list)

        # 防御编程，防止前端传入 username
        if validated_data.get("username"):
            validated_data.pop("username")

        extra_fields = {key: value for key, value in request.data.items() if key not in validated_data}
        if extra_fields:
            validated_data["extras"] = {key: value for key, value in extra_fields.items()}

        unknown_fields = set(extra_fields.keys()) - set([x["name"] for x in fields if not x["builtin"]])  # noqa
        if unknown_fields:
            raise error_codes.UNKNOWN_FIELD.f(",".join(list(unknown_fields)))

        api_instance = bkuser_sdk.ProfilesApi(self.get_api_client_by_request(request))
        profile = api_instance.v2_profiles_partial_update(
            lookup_value=profile_id, lookup_field="id", body=validated_data
        )
        return ResponseParams(profile, {"context": {"request": request}})

    @inject_serializer(
        query_in=serializers.ListProfilesSerializer, out=serializers.ProfileResultSerializer, tags=["profiles"]
    )
    def list(self, request, category_id, validated_data):
        params = {
            "page": validated_data["page"],
            "page_size": validated_data["page_size"],
            "lookup_field": "category_id",
            "exact_lookups": [category_id],
        }

        keyword = validated_data.get("keyword")
        if keyword:
            params.update({"wildcard_search": keyword, "wildcard_search_fields": ["username", "display_name", "id"]})

        api_instance = bkuser_sdk.ProfilesApi(
            self.get_api_client_by_request(request, force_action_id=ActionEnum.VIEW_DEPARTMENT.value)
        )
        profiles = api_instance.v2_profiles_list(**params)

        return ResponseParams(profiles, {"context": {"request": request}})

    # TODO: 动态字段定义到swagger输出
    @inject_serializer(out=serializers.ProfileSerializer(), tags=["profiles"])
    def retrieve(self, request, profile_id):
        api_instance = bkuser_sdk.ProfilesApi(self.get_api_client_by_request(request))
        profile = api_instance.v2_profiles_read(profile_id, lookup_field="id")

        api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request, no_auth=True))
        fields = self.get_paging_results(api_instance.v2_dynamic_fields_list)
        extra_fields = [x for x in fields if not x["builtin"]]

        serializer = serializers.ProfileSerializer(profile, context={"request": request})
        return expand_extra_fields(extra_fields, serializer.data)

    @inject_serializer(
        body_in=serializers.UpdateProfileSerializer(many=True),
        out=serializers.ProfileSerializer(many=True),
        tags=["profiles"],
    )
    def multiple_update(self, request, validated_data):
        api_instance = bkuser_sdk.BatchApi(self.get_api_client_by_request(request))
        updated_profiles = api_instance.v2_batch_profiles_partial_update(body=validated_data)
        return ResponseParams(updated_profiles, {"context": {"request": request}})

    @inject_serializer(body_in=serializers.UpdateProfileSerializer(many=True), tags=["profiles"])
    def multiple_delete(self, request, validated_data):
        api_instance = bkuser_sdk.BatchApi(self.get_api_client_by_request(request))
        api_instance.v2_batch_profiles_delete(body=validated_data)
        return Response()
