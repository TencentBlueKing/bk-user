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
from django.http import HttpResponse
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template
from django.template.response import TemplateResponse

from .proxy import BkUserApiProxy
from bkuser_shell.common.error_codes import error_codes

# FIXME:
# 1. 推动前端切换到新版api
# 2. 全局使用同一个 ProxyViewSet.request


class HealthzViewSet(BkUserApiProxy):
    permission_classes: list = []

    def list(self, request):
        return self.do_proxy(request)

    def pong(self, request):
        return HttpResponse(content="pong")


class SiteFooterViewSet(BkUserApiProxy):
    permission_classes: list = []

    def get(self, request):
        """获取动态的 header & footer 内容"""
        return self.do_proxy(request, rewrite_path="/api/v1/web/site/footer/")


class WebPageViewSet(BkUserApiProxy):
    serializer_class = None
    permission_classes: list = []

    def index(self, request):
        try:
            return TemplateResponse(request=request, template=get_template("index.html"))
        except TemplateDoesNotExist:
            raise error_codes.CANNOT_FIND_TEMPLATE


class SyncTaskViewSet(BkUserApiProxy):
    def list(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/sync_tasks/")


class SyncTaskLogViewSet(BkUserApiProxy):
    def list(self, request, *args, **kwargs):
        # FIXME: use a func to do re-map
        api_path = BkUserApiProxy.get_api_path(request)
        # in: /api/v2/sync_task/4a3cbc71-8141-4f1a-b306-f723d0224d44/logs
        # out: /api/v1/web/sync_tasks/4a3cbc71-8141-4f1a-b306-f723d0224d44/progresses/
        api_path = api_path.replace("/api/v2/sync_task/", "/api/v1/web/sync_tasks/")
        api_path = api_path.replace("/logs", "/progresses/")
        return self.do_proxy(request, rewrite_path=api_path)


class GeneralLogViewSet(BkUserApiProxy):
    def list(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/audits/logs/types/general/")


class LoginLogViewSet(BkUserApiProxy):
    def list(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/audits/logs/types/login/")


class LoginLogExportViewSet(BkUserApiProxy):
    def list(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/audits/logs/types/login/operations/export/")


class FieldsManageableViewSet(BkUserApiProxy):
    def get(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/fields/manageable/")


class FieldsVisibleViewSet(BkUserApiProxy):
    def patch(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/fields/visible/")


class FieldsOrderViewSet(BkUserApiProxy):
    def patch(self, request, *args, **kwargs):
        # FIXME: use a func to do re-map
        api_path = BkUserApiProxy.get_api_path(request)
        # in: /api/v2/fields/13/order/5/
        # out: /api/v1/web/fields/13/order/5/
        api_path = api_path.replace("/api/v2/fields/", "/api/v1/web/fields/")
        return self.do_proxy(request, rewrite_path=api_path)


class FieldsViewSet(BkUserApiProxy):
    def list(self, request, *args, **kwargs):
        """获取所有用户字段"""
        return self.do_proxy(request, rewrite_path="/api/v1/web/fields/")

    def create(self, request, *args, **kwargs):
        """创建用户字段"""
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/fields/", "/api/v1/web/fields/")
        return self.do_proxy(request, rewrite_path=api_path)

    def update(self, request, *args, **kwargs):
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/fields/", "/api/v1/web/fields/")
        return self.do_proxy(request, rewrite_path=api_path)

    def delete(self, request, *args, **kwargs):
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/fields/", "/api/v1/web/fields/")
        return self.do_proxy(request, rewrite_path=api_path)


class LoginInfoViewSet(BkUserApiProxy):
    def get(self, request, *args, **kwargs):
        username = request.user.username
        return self.do_proxy(request, rewrite_path=f"/api/v1/web/profiles/me/?username={username}")


class CategoryMetasViewSet(BkUserApiProxy):
    def get(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/categories/metas/")


class SettingsMetasViewSet(BkUserApiProxy):
    def get(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/settings/metas/")


class DepartmentSearchViewSet(BkUserApiProxy):
    def get(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/departments/search/")


class ProfilesSearchViewSet(BkUserApiProxy):
    def get(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/profiles/search/")


class CategoriesTestConnectionViewSet(BkUserApiProxy):
    def post(self, request, *args, **kwargs):
        # in:  /api/v2/categories/3/test_connection/
        # out: /api/v1/web/categories/3/operations/test_connection/
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/categories/", "/api/v1/web/categories/")
        api_path = api_path.replace("test_connection/", "operations/test_connection/")
        return self.do_proxy(request, rewrite_path=api_path)


class CategoriesTestFetchDataViewSet(BkUserApiProxy):
    def post(self, request, *args, **kwargs):
        # in:  /api/v2/categories/3/test_fetch_data/
        # out: /api/v1/web/categories/3/operations/test_connection/
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/categories/", "/api/v1/web/categories/")
        api_path = api_path.replace("test_fetch_data/", "operations/test_fetch_data/")
        return self.do_proxy(request, rewrite_path=api_path)


class CategoriesExportTemplateViewSet(BkUserApiProxy):
    def get(self, request, *args, **kwargs):
        # in:  /api/v2/categories/3/export_template/
        # out: /api/v1/web/categories/3/operations/export_template/
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/categories/", "/api/v1/web/categories/")
        api_path = api_path.replace("export_template/", "operations/export_template/")
        return self.do_proxy(request, rewrite_path=api_path)


class CategoriesExportViewSet(BkUserApiProxy):
    def get(self, request, *args, **kwargs):
        # in:  /api/v2/categories/3/export/
        # out: /api/v1/web/categories/3/operations/export/
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/categories/", "/api/v1/web/categories/")
        api_path = api_path.replace("export/", "operations/export/")
        return self.do_proxy(request, rewrite_path=api_path)


class CategoryListCreateViewSet(BkUserApiProxy):
    def list(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/categories/")

    def create(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/categories/")


class CategoryUpdateDeleteViewSet(BkUserApiProxy):
    def update(self, request, *args, **kwargs):
        api_path = BkUserApiProxy.get_api_path(request)
        # in: /api/v2/categories/5/
        # out: /api/v1/web/categories/5/
        api_path = api_path.replace("/api/v2/categories/", "/api/v1/web/categories/")
        return self.do_proxy(request, rewrite_path=api_path)

    def delete(self, request, *args, **kwargs):
        api_path = BkUserApiProxy.get_api_path(request)
        # in: /api/v2/categories/5/
        # out: /api/v1/web/categories/5/
        api_path = api_path.replace("/api/v2/categories/", "/api/v1/web/categories/")
        return self.do_proxy(request, rewrite_path=api_path)


class CategoriesSyncViewSet(BkUserApiProxy):
    def post(self, request, *args, **kwargs):
        # in: /api/v2/categories/5/sync/
        # out: /api/v1/web/categories/5/operations/sync_or_import/
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/categories/", "/api/v1/web/categories/")
        api_path = api_path.replace("sync/", "operations/sync_or_import/")
        return self.do_proxy(request, rewrite_path=api_path)


class CategoriesSwitchOrderViewSet(BkUserApiProxy):
    def patch(self, request, *args, **kwargs):
        # in: /api/v2/categories/5/switch_order/13/
        # out: /api/v1/web/categories/5/operations/switch_order/13/
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/categories/", "/api/v1/web/categories/")
        api_path = api_path.replace("switch_order/", "operations/switch_order/")
        return self.do_proxy(request, rewrite_path=api_path)


class DepartmentRetrieveUpdateDeleteViewSet(BkUserApiProxy):
    def request(self, request, *args, **kwargs):
        api_path = BkUserApiProxy.get_api_path(request)
        # in: /api/v2/departments/1/
        # out: /api/v1/web/departments/1/
        api_path = api_path.replace("/api/v2/departments/", "/api/v1/web/departments/")
        return self.do_proxy(request, rewrite_path=api_path)


class DepartmentSwitchOrderViewSet(BkUserApiProxy):
    def patch(self, request, *args, **kwargs):
        # in: /api/v2/departments/5/switch_order/13/
        # out: /api/v1/web/departments/5/operations/switch_order/13/
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/departments/", "/api/v1/web/departments/")
        api_path = api_path.replace("switch_order/", "operations/switch_order/")
        return self.do_proxy(request, rewrite_path=api_path)


class CategorySettingsNamespaceViewSet(BkUserApiProxy):
    def request(self, request, *args, **kwargs):
        # in: api/v2/categories/%s/settings/namespaces/%s/
        # out: api/v1/web/categories/%s/settings/namespaces/%s/
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/categories/", "/api/v1/web/categories/")
        return self.do_proxy(request, rewrite_path=api_path)


class CategorySettingsListViewSet(BkUserApiProxy):
    def list(self, request, *args, **kwargs):
        # in: api/v2/categories/%s/settings/
        # out: api/v1/web/categories/%s/settings/
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/categories/", "/api/v1/web/categories/")
        return self.do_proxy(request, rewrite_path=api_path)


class CategoryProfilesViewSet(BkUserApiProxy):
    def list(self, request, *args, **kwargs):
        # in: api/v2/categories/%s/profiles/
        # out: api/v1/web/categories/%s/profiles/
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/categories/", "/api/v1/web/categories/")
        return self.do_proxy(request, rewrite_path=api_path)


class CategoryDepartmentsViewSet(BkUserApiProxy):
    def list(self, request, *args, **kwargs):
        api_path = BkUserApiProxy.get_api_path(request)
        # in: /api/v2/categories/13/departments/search/?keyword=a&max_items=40&with_ancestors=true
        # out: /api/v1/web/categories/1/13/departments/?keyword=a&max_items=40&with_ancestors=true
        # NOTE: 区别: 1. with_ancestors=true无效 2. max_items无效需要改成page_size(并且加上page)
        api_path = api_path.replace("/api/v2/categories/", "/api/v1/web/categories/")
        api_path = api_path.replace("departments/search/", "departments/")
        return self.do_proxy(request, rewrite_path=api_path)


class ProfilesRetrieveUpdateViewSet(BkUserApiProxy):
    def request(self, request, *args, **kwargs):
        api_path = BkUserApiProxy.get_api_path(request)
        # in: /api/v2/profiles/1/
        # out: /api/v1/web/profiles/1/
        api_path = api_path.replace("/api/v2/profiles/", "/api/v1/web/profiles/")
        return self.do_proxy(request, rewrite_path=api_path)


class ProfilesRestorationViewSet(BkUserApiProxy):
    def post(self, request, *args, **kwargs):
        api_path = BkUserApiProxy.get_api_path(request)
        # in: /api/v2/profiles/1/restoration/
        # out: /api/v1/web/profiles/1/restoration/
        api_path = api_path.replace("/api/v2/profiles/", "/api/v1/web/profiles/")
        api_path = api_path.replace("restoration/", "operations/restoration/")
        return self.do_proxy(request, rewrite_path=api_path)


class DepartmentProfilesViewSet(BkUserApiProxy):
    def request(self, request, *args, **kwargs):
        # in: api/v2/departments/%s/profiles/
        # out: api/v1/web/departments/%s/profiles/
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/departments/", "/api/v1/web/departments/")

        return self.do_proxy(request, rewrite_path=api_path)


class ProfileCreateViewSet(BkUserApiProxy):
    def post(self, request, *args, **kwargs):
        api_path = BkUserApiProxy.get_api_path(request)
        # in: /api/v2/profiles/
        # out: /api/v1/web/profiles/
        api_path = api_path.replace("/api/v2/profiles/", "/api/v1/web/profiles/")
        return self.do_proxy(request, rewrite_path=api_path)


class SearchViewSet(BkUserApiProxy):
    def get(self, request, *args, **kwargs):
        # in: /api/v2/search/detail/
        # out: /api/v1/web/search/
        return self.do_proxy(request, rewrite_path="/api/v1/web/search/")


class DepartmentViewSet(BkUserApiProxy):
    def get(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/home/tree/")

    def post(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/departments/")


class ProfilesBatchViewSet(BkUserApiProxy):
    def request(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/profiles/batch/")
