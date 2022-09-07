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

from django.conf import settings
from django.utils.translation import gettext as _
from openpyxl import load_workbook
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import (
    CategoryCreateSerializer,
    CategoryDetailSerializer,
    CategoryMetaSerializer,
    CategorySettingListSerializer,
    CategorySettingSerializer,
    CategoryTestConnectionSerializer,
    CategoryTestFetchDataSerializer,
    CategoryUpdateSerializer,
)
from bkuser_core.api.web.export import ProfileExcelExporter
from bkuser_core.api.web.field.serializers import FieldSerializer
from bkuser_core.api.web.utils import get_category, get_username, list_setting_metas
from bkuser_core.bkiam.exceptions import IAMPermissionDenied
from bkuser_core.bkiam.permissions import IAMAction, IAMPermissionExtraInfo, ManageCategoryPermission, Permission
from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.loader import get_plugin_by_category
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.categories.signals import post_category_create, post_category_delete
from bkuser_core.common.error_codes import error_codes
from bkuser_core.profiles.models import DynamicFieldInfo
from bkuser_core.user_settings.models import Setting

logger = logging.getLogger(__name__)


# FIXME: 统一加
# @audit_general_log(operate_type=OperationType.DELETE.value)


class CategoryMetasListApi(generics.ListAPIView):
    @classmethod
    def make_meta(cls, type_: CategoryType):
        return {
            "type": type_,
            "description": CategoryType.get_description(type_),
            "name": CategoryType.get_choice_label(type_),
        }

    def get(self, request, *args, **kwargs):
        """
        列表展示所有目录类型基本信息
        """
        metas = []
        for type_ in CategoryType.all():
            # 这里目前只返回创建目录类型的权限操作，后期应该可扩展
            try:
                action_id = IAMAction.get_action_by_category_type(type_)
            except KeyError:
                continue

            _meta = self.make_meta(type_)
            # Q：为什么这里需要手动判断权限，而不是通用 permission_classes？
            # A：因为这里的资源（目录类型）是没有对应实体，同时也没有在权限中心注册
            username = get_username(request)
            if not Permission().allow_action_without_resource(username, action_id):
                _meta.update(
                    {
                        "authorized": False,
                        "extra_info": IAMPermissionExtraInfo.from_actions(
                            username=username, action_ids=[action_id]
                        ).to_dict(),
                    }
                )
            metas.append(_meta)

        return Response(CategoryMetaSerializer(metas, many=True).data)


class CategorySettingListApi(generics.ListAPIView):
    serializer_class = CategorySettingSerializer
    permission_classes = [ManageCategoryPermission]

    def get_queryset(self):
        slz = CategorySettingListSerializer(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        category_id = self.kwargs["id"]
        category = get_category(category_id)
        namespace = data.get("namespace")
        region = data.get("region")
        metas = list_setting_metas(category.type, region, namespace)
        return Setting.objects.filter(meta__in=metas, category_id=category_id)


class CategoryListCreateApi(generics.ListCreateAPIView):
    serializer_class = CategoryDetailSerializer

    # TODO: 产品上应该返回全部列表, 展示这个人哪些有权限/哪些没权限
    # 而不是, 只返回有权限的
    def get_queryset(self):
        username = get_username(self.request)

        queryset = ProfileCategory.objects.filter(enabled=True)
        if settings.ENABLE_IAM:
            fs = Permission().make_filter_of_category(username, IAMAction.VIEW_CATEGORY)
            queryset = queryset.filter(fs)

        return queryset

    def post(self, request, *args, **kwargs):
        """
        创建用户目录
        """
        serializer = CategoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # check permission
        username = get_username(request)
        action_id = IAMAction.get_action_by_category_type(data["type"])
        if not Permission().allow_action_without_resource(username, action_id):
            raise IAMPermissionDenied(
                detail=_("您没有权限进行该操作，请在权限中心申请。"),
                extra_info=IAMPermissionExtraInfo.from_raw_params(username, action_id).to_dict(),
            )

        instance = serializer.save()

        # 默认添加到最后 TODO: 需要一个更优雅的实现
        max_order = ProfileCategory.objects.get_max_order()
        instance.order = max_order + 1
        instance.save(update_fields=["order"])
        post_category_create.send_robust(
            sender=self, instance=instance, operator=request.operator, extra_values={"request": request}
        )
        return Response(CategoryDetailSerializer(instance).data, status=status.HTTP_201_CREATED)


class CategoryUpdateDeleteApi(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [ManageCategoryPermission]

    queryset = ProfileCategory.objects.all()
    lookup_url_kwarg = "id"

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CategoryUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(CategoryDetailSerializer(instance).data)

    def delete(self, request, *args, **kwargs):
        """删除用户目录"""
        instance = self.get_object()
        if instance.default:
            raise error_codes.CANNOT_DELETE_DEFAULT_CATEGORY

        # 依赖 model 的 delete 方法, 执行软删除
        instance.delete()
        post_category_delete.send_robust(sender=self, instance=instance, operator=request.operator)
        return Response(status=status.HTTP_200_OK)


class CategoryOperationTestConnectionApi(generics.CreateAPIView):
    permission_classes = [ManageCategoryPermission]

    queryset = ProfileCategory.objects.all()
    lookup_url_kwarg = "id"

    def post(self, request, *args, **kwargs):
        """测试连接"""
        serializer = CategoryTestConnectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = self.get_object()
        if instance.type not in [CategoryType.MAD.value, CategoryType.LDAP.value]:
            raise error_codes.TEST_CONNECTION_UNSUPPORTED

        # NOTE: 过于复杂, 在重构同步模块时, 更新这里的代码
        try:
            syncer_cls = get_plugin_by_category(instance).syncer_cls
        except Exception:
            logger.exception(
                "category<%s-%s-%s> load ldap client failed",
                instance.type,
                instance.display_name,
                instance.id,
            )
            raise error_codes.LOAD_LDAP_CLIENT_FAILED

        try:
            syncer_cls(instance.id, with_initialize_client=False).fetcher.client.initialize(
                **serializer.validated_data
            )
        except Exception as e:
            logger.exception(
                "failed to test initialize category<%s-%s-%s>", instance.type, instance.display_name, instance.id
            )
            raise error_codes.TEST_CONNECTION_FAILED.format(str(e), replace=True)

        return Response()


class CategoryOperationTestFetchDataApi(generics.CreateAPIView):
    permission_classes = [ManageCategoryPermission]

    queryset = ProfileCategory.objects.all()
    lookup_url_kwarg = "id"

    def post(self, request, *args, **kwargs):
        """测试获取数据"""
        serializer = CategoryTestFetchDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = self.get_object()
        if instance.type not in [CategoryType.MAD.value, CategoryType.LDAP.value]:
            raise error_codes.TEST_CONNECTION_UNSUPPORTED

        try:
            syncer_cls = get_plugin_by_category(instance).syncer_cls
        except Exception:
            logger.exception(
                "category<%s-%s-%s> load data adapter failed",
                instance.type,
                instance.display_name,
                instance.id,
            )
            raise error_codes.LOAD_DATA_ADAPTER_FAILED

        try:
            syncer = syncer_cls(instance.id)
        except Exception as e:
            logger.exception(
                "failed to test initialize category<%s-%s-%s>", instance.type, instance.display_name, instance.id
            )
            raise error_codes.TEST_CONNECTION_FAILED.f(f"请确保连接设置正确 {str(e)}")

        try:
            syncer.fetcher.test_fetch_data(serializer.validated_data)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(
                "failed to fetch data from category<%s-%s-%s>", instance.type, instance.display_name, instance.id
            )
            error_detail = f" ({type(e).__module__}.{type(e).__name__}: {str(e)})"
            raise error_codes.TEST_FETCH_DATA_FAILED.f(error_detail)

        return Response()


class CategoryOperationExportTemplateApi(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        """生成excel导入模板样例文件"""
        # api_instance = bkuser_sdk.DynamicFieldsApi(self.get_api_client_by_request(request))
        # fields = self.get_paging_results(api_instance.v2_dynamic_fields_list)
        fields = DynamicFieldInfo.objects.filter(enabled=True).all()
        data = FieldSerializer(fields, many=True).data
        exporter = ProfileExcelExporter(
            load_workbook(settings.EXPORT_ORG_TEMPLATE), settings.EXPORT_EXCEL_FILENAME + "_org_tmpl", data
        )

        return exporter.to_response()
