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
from bkuser.biz.tenant_admin import (
    get_data_sources_info_by_tenant_id,
    get_email_by_manager_id,
    get_manager_ids_by_tenant_id,
    get_managers_info_by_manager_ids,
    get_telephone_by_manager_id,
)
from rest_framework import serializers


class TenantSearchSLZ(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class TenantOutputSLZ(serializers.Serializer):
    create_time = serializers.CharField()
    id = serializers.CharField()
    name = serializers.CharField()
    enabled_user_count_display = serializers.BooleanField()
    # TODO:child
    managers = serializers.SerializerMethodField()
    data_sources = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()

    def get_managers(self, obj):
        manager_ids = get_manager_ids_by_tenant_id(tenant_id=obj.id)
        managers_info = get_managers_info_by_manager_ids(manager_ids=manager_ids)

        managers = [
            {
                "id": m["id"],
                "username": m["username"],
                "display_name": m["display_name"],
                "email": get_email_by_manager_id(manager_id=m["id"]),
                "telephone": get_telephone_by_manager_id(manager_id=m["id"]),
            }
            for m in managers_info
        ]

        return managers

    def get_data_sources(self, obj):
        data_sources_info = get_data_sources_info_by_tenant_id(tenant_id=obj.id)

        data_sources = [{"id": d["id"], "name": d["name"]} for d in data_sources_info]
        return data_sources

    def get_logo(self, obj):
        pass
