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
from typing import List

from bkuser_core.audit.constants import OperationEnum
from bkuser_core.audit.utils import create_general_log
from bkuser_core.bkiam.permissions import IAMAction, IAMHelper, IAMPermissionExtraInfo, need_iam
from bkuser_core.categories.constants import CategoryType, SyncTaskType
from bkuser_core.categories.exceptions import ExistsSyncingTaskError, FetchDataFromRemoteFailed
from bkuser_core.categories.loader import get_plugin_by_category
from bkuser_core.categories.models import ProfileCategory, SyncTask
from bkuser_core.categories.plugins.local.exceptions import DataFormatError
from bkuser_core.categories.serializers import (
    CategoryMetaSLZ,
    CategorySerializer,
    CategorySyncResponseSLZ,
    CategorySyncSerializer,
    CategoryTestConnectionSerializer,
    CategoryTestFetchDataSerializer,
    CreateCategorySerializer,
    SyncTaskProcessSerializer,
    SyncTaskSerializer,
)
from bkuser_core.categories.signals import post_category_create, post_category_delete
from bkuser_core.categories.tasks import adapter_sync
from bkuser_core.common.cache import clear_cache_if_succeed
from bkuser_core.common.error_codes import CoreAPIError, error_codes
from bkuser_core.common.serializers import EmptySerializer
from bkuser_core.common.viewset import AdvancedListAPIView, AdvancedModelViewSet, AdvancedSearchFilter
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class CategoryViewSet(AdvancedModelViewSet, AdvancedListAPIView):
    queryset = ProfileCategory.objects.filter()
    serializer_class = CategorySerializer
    lookup_field = "id"
    filter_backends = [
        AdvancedSearchFilter,
        filters.OrderingFilter,
    ]

    iam_filter_actions = ("list",)

    @swagger_auto_schema(
        responses={"200": CategoryMetaSLZ(many=True)},
        tags=["categories"],
        operation_id="v2_categories_list_metas",
    )
    def list_metas(self, request):
        """
        列表展示所有目录类型基本信息
        """
        helper = IAMHelper()

        def make_meta(type_: CategoryType):
            return {
                "type": type_,
                "description": CategoryType.get_description(type_),
                "name": CategoryType.get_choice_label(type_),
            }

        metas = []
        for type_ in CategoryType.all():
            # 这里目前只返回创建目录类型的权限操作，后期应该可扩展
            try:
                action_id = IAMAction.get_action_by_category_type(type_)
            except KeyError:
                # tof 属于隐藏目录，这里直接忽略掉
                continue

            _meta = make_meta(type_)
            # Q：为什么这里需要手动判断权限，而不是通用 permission_classes？
            # A：因为这里的资源（目录类型）是没有对应实体，同时也没有在权限中心注册
            if need_iam(request) and not helper.action_allow(request.operator, action_id):
                _meta.update(
                    {
                        "authorized": False,
                        "extra_info": IAMPermissionExtraInfo.from_actions(
                            username=request.operator, action_ids=[action_id]
                        ).to_dict(),
                    }
                )
            metas.append(_meta)

        return Response(CategoryMetaSLZ(metas, many=True).data)

    @method_decorator(clear_cache_if_succeed)
    @swagger_auto_schema(request_body=CreateCategorySerializer, responses={"200": CategorySerializer()})
    def create(self, request, *args, **kwargs):
        """
        创建用户目录
        """
        self.check_permissions(request)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        headers = self.get_success_headers(serializer.data)

        # 默认添加到最后 TODO: 需要一个更优雅的实现
        max_order = ProfileCategory.objects.get_max_order()
        instance.order = max_order + 1
        instance.save(update_fields=["order"])

        post_category_create.send(sender=self, category=instance, creator=request.operator)
        create_general_log(
            operator=request.operator,
            operate_type=OperationEnum.CREATE.value,
            operator_obj=instance,
            request=request,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer(self, *args, **kwargs):
        if self.action in ["create"]:
            return CreateCategorySerializer(*args, **kwargs)
        else:
            return self.serializer_class(*args, **kwargs)

    @method_decorator(clear_cache_if_succeed)
    def update(self, request, *args, **kwargs):
        """
        更新用户目录
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        self.check_object_permissions(request, instance)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        updating_domain = serializer.validated_data.get("domain")
        if updating_domain and not updating_domain == instance.domain:
            raise error_codes.CANNOT_UPDATE_DOMAIN

        if instance.default and any(serializer.validated_data.get(x) is False for x in ["enabled", "status"]):
            raise error_codes.CANNOT_DISABLE_DOMAIN

        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        create_general_log(
            operator=request.operator,
            operate_type=OperationEnum.UPDATE.value,
            operator_obj=instance,
            request=request,
        )

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        删除用户目录
        """
        instance = self.get_object()
        if instance.default:
            raise error_codes.CANNOT_DELETE_DEFAULT_CATEGORY

        post_category_delete.send(sender=self, category=instance, operator=request.operator)
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=CategoryTestConnectionSerializer,
        responses={"200": EmptySerializer()},
    )
    def test_connection(self, request, lookup_value):
        """测试连接"""
        serializer = CategoryTestConnectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = self.get_object()
        self.check_object_permissions(request, instance)

        if instance.type not in [CategoryType.MAD.value, CategoryType.LDAP.value]:
            raise error_codes.TEST_CONNECTION_UNSUPPORTED

        try:
            category_config = get_plugin_by_category(instance)
            client_class = import_string(category_config.extra_config["ldap_client"])
        except Exception:
            logger.exception(
                "category<%s-%s-%s> load ldap client failed",
                instance.type,
                instance.display_name,
                instance.id,
            )
            raise error_codes.LOAD_LDAP_CLIENT_FAILED

        try:
            client_class.initialize(**serializer.validated_data)
        except Exception:
            logger.exception("failed to test initialize category<%s>", instance.id)
            raise error_codes.TEST_CONNECTION_FAILED

        return Response()

    @swagger_auto_schema(
        request_body=CategoryTestFetchDataSerializer,
        responses={"200": EmptySerializer()},
    )
    def test_fetch_data(self, request, lookup_value):
        """测试获取数据"""
        serializer = CategoryTestFetchDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = self.get_object()
        self.check_object_permissions(request, instance)

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
        except Exception:
            logger.exception("failed to test initialize category<%s>", instance.id)
            raise error_codes.TEST_CONNECTION_FAILED.f("请确保连接设置正确")

        try:
            syncer.fetcher.test_fetch_data(serializer.validated_data)
        except FetchDataFromRemoteFailed as e:
            raise error_codes.TEST_FETCH_DATA_FAILED.f(f"{e}")
        except Exception:  # pylint: disable=broad-except
            raise error_codes.TEST_FETCH_DATA_FAILED

        return Response()

    @method_decorator(clear_cache_if_succeed)
    @swagger_auto_schema(request_body=CategorySyncSerializer, responses={"200": CategorySyncResponseSLZ()})
    def sync(self, request, lookup_value):
        """同步目录"""
        instance: ProfileCategory = self.get_object()
        self.check_object_permissions(request, instance)

        if instance.type == CategoryType.LOCAL.value:
            raise error_codes.LOCAL_CATEGORY_CANNOT_SYNC

        try:
            task_id = SyncTask.objects.register_task(
                category=instance, operator=request.operator, type_=SyncTaskType.MANUAL
            ).id
        except ExistsSyncingTaskError as e:
            raise error_codes.LOAD_DATA_FAILED.f(str(e))

        try:
            adapter_sync.apply_async(
                kwargs={"instance_id": instance.id, "operator": request.operator, "task_id": task_id}
            )
        except FetchDataFromRemoteFailed as e:
            logger.exception("failed to sync data")
            raise error_codes.SYNC_DATA_FAILED.f(f"{e}")
        except CoreAPIError:
            raise
        except Exception:
            logger.exception("failed to sync data")
            raise error_codes.SYNC_DATA_FAILED

        create_general_log(
            operator=request.operator,
            operate_type=OperationEnum.SYNC.value,
            operator_obj=instance,
            request=request,
        )
        return Response({"task_id": task_id})


class CategoryFileViewSet(AdvancedModelViewSet, AdvancedListAPIView):
    queryset = ProfileCategory.objects.filter(enabled=True)
    serializer_class = CategorySerializer
    parser_classes: List = [MultiPartParser, FormParser]
    lookup_field = "id"
    ordering = ["-create_time"]

    @method_decorator(clear_cache_if_succeed)
    @swagger_auto_schema(request_body=CategorySyncSerializer, responses={"200": EmptySerializer()})
    def import_data_file(self, request, lookup_value):
        """向本地目录导入数据文件"""
        serializer = CategorySyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        self.check_object_permissions(request, instance)

        if instance.type != CategoryType.LOCAL.value:
            raise error_codes.CATEGORY_CANNOT_IMPORT_BY_FILE

        try:
            task_id = SyncTask.objects.register_task(
                category=instance, operator=request.operator, type_=SyncTaskType.MANUAL
            ).id
        except ExistsSyncingTaskError as e:
            raise error_codes.LOAD_DATA_FAILED.f(str(e))

        params = {"raw_data_file": serializer.validated_data["raw_data_file"]}
        try:
            # TODO: FileField 可能不能反序列化, 所以可能不能传到 celery 执行
            adapter_sync(lookup_value, operator=request.operator, task_id=task_id, **params)
        except DataFormatError as e:
            logger.exception("failed to sync data")
            raise error_codes.SYNC_DATA_FAILED.format(str(e), replace=True)
        except Exception as e:
            logger.exception("failed to sync data")
            raise error_codes.SYNC_DATA_FAILED.format(str(e), replace=True)

        create_general_log(
            operator=request.operator,
            operate_type=OperationEnum.IMPORT.value,
            operator_obj=instance,
            request=request,
        )
        return Response()


class SyncTaskViewSet(AdvancedModelViewSet, AdvancedListAPIView):
    queryset = SyncTask.objects.all()
    serializer_class = SyncTaskSerializer
    lookup_field = "id"
    ordering = ["-create_time"]
    filter_backends = [
        AdvancedSearchFilter,
        filters.OrderingFilter,
    ]

    iam_filter_actions = ("list",)

    @action(methods=["GET"], detail=True)
    @swagger_auto_schema(responses={200: SyncTaskProcessSerializer(many=True)})
    def show_logs(self, request, lookup_value):
        task: SyncTask = self.get_object()
        processes = task.progresses.order_by("-create_time")

        slz = SyncTaskProcessSerializer(processes, many=True)
        return Response(slz.data)
