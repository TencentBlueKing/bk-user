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

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import ValidationError

from bkuser_core.api.web.serializers import StringArrayField
from bkuser_core.api.web.utils import get_extras_with_default_values
from bkuser_core.bkiam.serializers import AuthInfoSLZ
from bkuser_core.categories.constants import CategoryStatus, CreateAbleCategoryType
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.categories.utils import change_periodic_sync_task_status
from bkuser_core.departments.models import Department
from bkuser_core.profiles.models import Profile
from bkuser_core.profiles.validators import validate_domain
from bkuser_core.user_settings.models import Setting

logger = logging.getLogger(__name__)


class ExtraInfoSerializer(serializers.Serializer):
    auth_infos = serializers.ListField(read_only=True, child=AuthInfoSLZ())
    callback_url = serializers.CharField(read_only=True)


class CategoryMetaOutputSLZ(serializers.Serializer):
    """用户目录基本信息"""

    type = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    authorized = serializers.BooleanField(read_only=True, default=True)
    extra_info = ExtraInfoSerializer(read_only=True, default={})


class CategorySettingOutputSLZ(serializers.ModelSerializer):
    """配置项"""

    # NOTE: 这里只包含这几个字段的原因是, 目前只有category settings拿, 没有其他地方用到
    # 其他地方用到, 可以实现更通用的 slz

    key = serializers.CharField(source="meta.key", required=False)
    namespace = serializers.CharField(source="meta.namespace", required=False)
    region = serializers.CharField(source="meta.region", required=False)
    value = serializers.JSONField()

    class Meta:
        model = Setting
        fields = ["key", "namespace", "region", "value", "enabled"]


class CategoryDetailOutputSLZ(serializers.ModelSerializer):
    configured = serializers.SerializerMethodField()
    unfilled_namespaces = serializers.SerializerMethodField(required=False)
    activated = serializers.SerializerMethodField()

    syncing = serializers.BooleanField(read_only=True, required=False, allow_null=True)

    def get_configured(self, obj) -> bool:
        return obj.configured

    def get_unfilled_namespaces(self, obj) -> List[str]:
        # NOTE: 每个category产生一次查询
        unfilled_nss = set(obj.get_unfilled_settings().values_list("namespace", flat=True))
        return list(unfilled_nss)

    def get_activated(self, obj) -> bool:
        # TODO: make this a model property?
        return obj.status == CategoryStatus.NORMAL.value

    class Meta:
        model = ProfileCategory
        fields = "__all__"


class CategoryCreateInputSLZ(serializers.Serializer):
    """用户目录 Serializer"""

    domain = serializers.CharField(max_length=64, label=_("登陆域"), validators=[validate_domain])
    display_name = serializers.CharField(max_length=64, label=_("目录名"))
    type = serializers.ChoiceField(default="local", choices=CreateAbleCategoryType.get_choices())

    activated = serializers.BooleanField(default=True)

    def validate(self, data):
        if ProfileCategory.objects.filter(domain=data["domain"]).exists():
            raise ValidationError(_("登陆域为 {} 的用户目录已存在").format(data["domain"]))
        return data

    def create(self, validated_data):
        # NOTE: 这里很特殊, 前端是activated, 需要转status
        # TODO: 应该全部统一成 status
        # TODO: validated_data里的activated变成status 这段逻辑使用 to_internal_value会更合适
        status = CategoryStatus.INACTIVE.value
        activated = validated_data.pop("activated")
        if activated:
            status = CategoryStatus.NORMAL.value

        validated_data["status"] = status

        category = ProfileCategory.objects.create(**validated_data)
        return category


class CategoryUpdateInputSLZ(serializers.Serializer):
    display_name = serializers.CharField(max_length=64, required=False)
    activated = serializers.BooleanField(default=True, required=False)
    description = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        # NOTE: 这里做了activated的转换, 所以需要自定义update => 能否整合model serializer复用原先的方法, 只需要处理activated
        should_updated_fields = []
        activated = validated_data.get("activated", None)
        if activated is not None:
            instance.status = CategoryStatus.NORMAL.value if activated else CategoryStatus.INACTIVE.value
            should_updated_fields.append("status")
            # 变更同步任务使能状态
            logger.info(
                "going to change periodic task status<%s> for Category-<%s>, the category type is %s",
                activated,
                instance.id,
                instance.type,
            )
            change_periodic_sync_task_status(instance.id, activated)

        display_name = validated_data.get("display_name")
        if display_name:
            instance.display_name = display_name
            should_updated_fields.append("display_name")

        description = validated_data.get("description")
        if description:
            instance.description = description
            should_updated_fields.append("description")

        if should_updated_fields:
            instance.save(update_fields=should_updated_fields)
        return instance


class CategoryTestConnectionInputSLZ(serializers.Serializer):
    connection_url = serializers.CharField()
    user = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    timeout_setting = serializers.IntegerField(required=False, default=120)
    use_ssl = serializers.BooleanField(default=False, required=False)


class CategoryTestFetchDataInputSLZ(serializers.Serializer):
    basic_pull_node = serializers.CharField()
    user_filter = serializers.CharField()
    organization_class = serializers.CharField()
    user_group_filter = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    user_member_of = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class CategoryExportInputSLZ(serializers.Serializer):
    department_ids = StringArrayField(required=False, help_text="部门id列表")


class SimpleDepartmentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()

    class Meta:
        model = Department
        fields = ("id", "name", "order", "full_name")


class CategoryExportProfileLeaderSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    username = serializers.CharField(read_only=True)
    display_name = serializers.CharField(read_only=True)


class CategoryExportProfileOutputSLZ(serializers.ModelSerializer):
    # 登录日志导出需要用到 bkuser_core.api.web.audit.serializers
    leader = CategoryExportProfileLeaderSerializer(many=True)
    departments = SimpleDepartmentSerializer(many=True, required=False)
    last_login_time = serializers.DateTimeField(required=False, read_only=True)

    extras = serializers.SerializerMethodField(required=False)

    def get_extras(self, obj) -> dict:
        """尝试从 context 中获取默认字段值"""
        return get_extras_with_default_values(obj.extras)

    class Meta:
        model = Profile
        exclude = ["password"]


class CategoryFileImportInputSLZ(serializers.Serializer):
    file = serializers.FileField(required=False)


class CategoryFileImportQuerySLZ(serializers.Serializer):
    is_overwrite = serializers.BooleanField(required=False, default=False)


class CategorySyncResponseOutputSLZ(serializers.Serializer):
    task_id = serializers.CharField(help_text="task_id for the sync job.")


class CategoryNamespaceSettingUpdateInputSLZ(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.JSONField()
    enabled = serializers.BooleanField(required=False, default=True)


class CategorySettingCreateInputSLZ(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.JSONField()
    # namespace = serializers.CharField(required=False)
    # region = serializers.CharField()
    # enabled = serializers.BooleanField(required=False, default=True)


class CategoryProfileListInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(required=False)
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=10)

    has_no_department = serializers.BooleanField(required=False, default=False)


class CategoryDepartmentListInputSLZ(serializers.Serializer):
    keyword = serializers.CharField(allow_blank=False)
    # 暂时不支持这个参数, 一律返回带ancestors
    # with_ancestors = serializers.BooleanField(default=False)
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=10)
