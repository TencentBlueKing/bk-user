# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS
Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.conf import settings
from iam.contrib.django.dispatcher import DjangoBasicResourceApiDispatcher
from iam.resource.provider import ListResult, ResourceProvider, SchemaResult

from .base import new_iam


class AppResourceProvider(ResourceProvider):
    def _list_apps(self):
        """应用列表"""
        apps = [
            {
                "id": app_code,
                "display_name": app_name,
            }
            for app_code, app_name in settings.BK_REQUIRED_ACCESS_CONTROLLED_APPS.items()
        ]
        return sorted(apps, key=lambda x: x['id'])

    def list_attr(self, **options):
        """
        app 资源没有属性，返回空
        """
        return ListResult(results=[], count=0)

    def list_attr_value(self, filter, page, **options):
        """
        app 资源没有属性，返回空
        """
        return ListResult(results=[], count=0)

    def list_instance(self, filter, page, **options):
        """
        app 无上层资源
        """
        apps = self._list_apps()
        results = apps[page.slice_from : page.slice_to]

        return ListResult(results=results, count=len(apps))

    def fetch_instance_info(self, filter, **options):
        """
        app 没有定义属性，只处理 filter 中的 ids 字段
        """
        apps = self._list_apps()

        # 过滤
        ids = []
        if filter.ids:
            ids = filter.ids

        results = [i for i in apps if i["id"] in ids]
        return ListResult(results=results, count=0)

    def list_instance_by_policy(self, filter, page, **options):
        """
        不是实现，不支持
        """
        return ListResult(results=[], count=0)

    def search_instance(self, filter, page, **options):
        """
        搜索
        """
        apps = self._list_apps()
        # 过滤
        keyword = filter.keyword
        if keyword:
            apps = [i for i in apps if keyword in i["id"] or keyword in i["display_name"]]

        results = apps[page.slice_from : page.slice_to]

        return ListResult(results=results, count=len(apps))

    def fetch_instance_list(self, filter, page, **options):
        """
        不支持
        """
        return ListResult(results=[], count=0)

    def fetch_resource_type_schema(self, **options):
        """
        不支持
        """
        return SchemaResult(properties={})


dispatcher = DjangoBasicResourceApiDispatcher(new_iam(), settings.BK_SYSTEM_ID_IN_IAM)
dispatcher.register("app", AppResourceProvider())
