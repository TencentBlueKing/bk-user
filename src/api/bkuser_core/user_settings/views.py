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

from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response

from bkuser_core.apis.v2.viewset import AdvancedListAPIView, AdvancedModelViewSet
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.cache import clear_cache_if_succeed
from bkuser_core.common.error_codes import error_codes
from bkuser_core.common.models import is_obj_needed_update
from bkuser_core.user_settings import serializers
from bkuser_core.user_settings.models import Setting, SettingMeta
from bkuser_core.user_settings.serializers import SettingUpdateSerializer
from bkuser_core.user_settings.signals import post_setting_create, post_setting_update
from bkuser_global.drf_crown.crown import inject_serializer

logger = logging.getLogger(__name__)


class SettingViewSet(AdvancedModelViewSet):
    """配置项"""

    queryset = Setting.objects.all()
    serializer_class = serializers.SettingSerializer
    lookup_field: str = "id"

    @staticmethod
    def _get_category(category_id: int):
        # 目前只匹配 category_id
        retrieve_params = {"pk": category_id}

        # 找到用户目录
        try:
            return ProfileCategory.objects.get(**retrieve_params)
        except Exception:
            logger.exception("cannot find category: %s", retrieve_params)
            raise error_codes.CANNOT_FIND_CATEGORY

    @staticmethod
    def _get_metas(category, validated_data):
        # 找到配置元信息
        try:
            metas = SettingMeta.objects.filter(category_type=category.type, **validated_data)
        except Exception:
            logger.exception("cannot find setting meta: [category=%s, data=%s]", category, validated_data)
            raise error_codes.CANNOT_FIND_SETTING_META

        return metas

    @swagger_auto_schema(query_serializer=serializers.SettingListSerializer())
    def list(self, request, *args, **kwargs):
        serializer = serializers.SettingListSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        category_id = validated_data.pop("category_id")
        category = self._get_category(category_id=category_id)

        metas = self._get_metas(category, validated_data)
        settings = Setting.objects.filter(meta__in=metas, category_id=category_id)
        return Response(data=serializers.SettingSerializer(settings, many=True).data)

    @method_decorator(clear_cache_if_succeed)
    @swagger_auto_schema(
        request_body=serializers.SettingCreateSerializer,
        responses={"200": serializers.SettingSerializer()},
    )
    def create(self, request, *args, **kwargs):
        serializer = serializers.SettingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        category = self._get_category(category_id=validated_data.pop("category_id"))
        value = validated_data.pop("value")

        metas = self._get_metas(category, validated_data)
        if metas.count() != 1:
            raise error_codes.CANNOT_FIND_SETTING_META

        try:
            # 暂时忽略已创建报错
            setting, _ = Setting.objects.update_or_create(meta=metas[0], value=value, category=category)
        except Exception:
            logger.exception("cannot create setting. [meta=%s, value=%s, category=%s]", metas[0], value, category)
            raise error_codes.CANNOT_CREATE_SETTING

        post_setting_create.send(
            sender=self, instance=setting, operator=request.operator, extra_values={"request": request}
        )
        return Response(serializers.SettingSerializer(setting).data, status=status.HTTP_201_CREATED)

    def _update(self, request, validated_data):
        instance = self.get_object()
        try:
            need_update = is_obj_needed_update(instance, validated_data)
        except ValueError:
            raise error_codes.CANNOT_UPDATE_SETTING

        if need_update:
            try:
                for k, v in validated_data.items():
                    setattr(instance, k, v)
                instance.save()
            except Exception:
                logger.exception("failed to update setting")
                raise error_codes.CANNOT_UPDATE_SETTING
            else:
                # 仅当更新成功时才发送信号
                post_setting_update.send(
                    sender=self,
                    instance=self.get_object(),
                    operator=request.operator,
                    extra_values={"request": request},
                )
        return instance

    @inject_serializer(body_in=SettingUpdateSerializer(), out=serializers.SettingSerializer)
    def update(self, request, validated_data, *args, **kwargs):
        return self._update(request, validated_data)

    @inject_serializer(body_in=SettingUpdateSerializer(), out=serializers.SettingSerializer)
    def partial_update(self, request, validated_data, *args, **kwargs):
        return self._update(request, validated_data)


class SettingMetaViewSet(AdvancedModelViewSet, AdvancedListAPIView):
    """配置信息"""

    queryset = SettingMeta.objects.all()
    serializer_class = serializers.SettingMetaSerializer
    lookup_field = "id"
