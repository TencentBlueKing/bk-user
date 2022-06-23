import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from bkuser_core.apis.v2.viewset import AdvancedListAPIView, AdvancedModelViewSet
from bkuser_core.common.error_codes import error_codes
from bkuser_core.common.models import is_obj_needed_update
from bkuser_core.global_settings.models import GlobalSettings, GlobalSettingsMeta
from bkuser_core.global_settings.v2 import serializers as local_serializers
from bkuser_core.user_settings.signals import post_setting_update
from bkuser_global.drf_crown import inject_serializer

logger = logging.getLogger(__name__)


class GlobalSettingModelViewSet(AdvancedModelViewSet):
    queryset = GlobalSettings.objects.all()
    serializer_class = local_serializers.GlobalSettingsSerializer
    lookup_field: str = "id"

    @staticmethod
    def _get_metas(validated_data):
        # 找到配置元信息
        try:
            metas = GlobalSettingsMeta.objects.filter(**validated_data)
        except Exception:
            logger.exception("cannot find global setting meta: [data=%s]", validated_data)
            raise error_codes.CANNOT_FIND_GLOBAL_SETTING_META
        return metas

    @swagger_auto_schema(
        query_serializer=local_serializers.GlobalSettingsListSerializer(),
        responses={"200": local_serializers.GlobalSettingsSerializer()},
    )
    def list(self, request, *args, **kwargs):
        serializer = local_serializers.GlobalSettingsListSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        metas = self._get_metas(validated_data)
        global_settings = GlobalSettings.objects.filter(meta__in=metas)
        return Response(data=local_serializers.GlobalSettingsSerializer(global_settings, many=True).data)

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
                logger.exception("failed to update global setting")
                raise error_codes.CANNOT_UPDATE_GLOBAL_SETTING
            else:
                # 仅当更新成功时才发送信号
                post_setting_update.send(
                    sender=self,
                    instance=self.get_object(),
                    operator=request.operator,
                    extra_values={"request": request},
                )
        return instance

    @inject_serializer(
        body_in=local_serializers.GlobalSettingsUpdateSerializer(), out=local_serializers.GlobalSettingsSerializer
    )
    def update(self, request, validated_data, *args, **kwargs):
        return self._update(request, validated_data)

    @inject_serializer(
        body_in=local_serializers.GlobalSettingsUpdateSerializer(), out=local_serializers.GlobalSettingsSerializer
    )
    def partial_update(self, request, validated_data, *args, **kwargs):
        return self._update(request, validated_data)


class GlobalSettingMetaViewSet(AdvancedModelViewSet, AdvancedListAPIView):
    """配置信息"""

    queryset = GlobalSettingsMeta.objects.all()
    serializer_class = local_serializers.GlobalSettingsMetaSerializer
    lookup_field = "id"
