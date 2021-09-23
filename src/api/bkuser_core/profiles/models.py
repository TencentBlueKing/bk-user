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
import datetime

import jsonfield
from bkuser_core.audit.constants import LogInFailReasonEnum
from bkuser_core.audit.models import AuditObjMetaInfo
from bkuser_core.common.bulk_update.manager import BulkUpdateManager
from bkuser_core.common.models import TimestampedModel
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from .constants import (
    TIME_ZONE_CHOICES,
    DynamicFieldTypeEnum,
    FieldMapMethod,
    LanguageEnum,
    PasswdValidityPeriodEnum,
    ProfileStatus,
    RoleCodeEnum,
    StaffStatus,
)
from .managers import DynamicFieldInfoManager, ProfileAllManager, ProfileManager, ProfileTokenManager
from .validators import validate_domain, validate_dynamic_field_name, validate_extras_value_unique, validate_username


class Profile(TimestampedModel):
    """用户表"""

    # ----------------------- 登录名相关 -----------------------
    username = models.CharField(verbose_name=_("用户名"), max_length=255, db_index=True)
    qq = models.CharField(verbose_name=_("QQ"), max_length=64, default="", blank=True)
    email = models.EmailField(verbose_name=_("邮箱"), null=True, blank=True, default="", max_length=255)
    telephone = models.CharField(verbose_name=_("手机号码"), null=True, blank=True, default="", max_length=255)
    wx_userid = models.CharField(verbose_name=_("微信ID"), null=True, blank=True, default="", max_length=255)
    wx_openid = models.CharField(verbose_name=_("微信公众号OpenID"), null=True, blank=True, default="", max_length=255)
    # ----------------------- 登录名相关 -----------------------

    # ----------------------- 同步相关 -----------------------
    code = models.CharField(
        verbose_name=_("标识"),
        max_length=64,
        db_index=True,
        unique=True,
        null=True,
        blank=True,
    )
    # ----------------------- 同步相关 -----------------------

    # ----------------------- 目录相关 -----------------------
    # 由写入时保证 domain & category_id 对应性
    domain = models.CharField(verbose_name=_("域"), max_length=64, null=True, blank=True, db_index=True)
    category_id = models.IntegerField(verbose_name=_("用户目录ID"), null=True, blank=True, db_index=True)
    # ----------------------- 目录相关 -----------------------

    display_name = models.CharField(verbose_name=_("全名"), null=True, blank=True, default="", max_length=255)
    logo = models.TextField(verbose_name=_("Avatar"), blank=True, null=True)

    # ----------------------- 状态相关 -----------------------
    status = models.CharField(
        verbose_name=_("账户状态"),
        choices=ProfileStatus.get_choices(),
        default=ProfileStatus.NORMAL.value,
        max_length=64,
    )
    staff_status = models.CharField(
        verbose_name=_("在职状态"),
        choices=StaffStatus.get_choices(),
        default=StaffStatus.IN.value,
        max_length=64,
    )
    # ----------------------- 状态相关 -----------------------

    # ----------------------- 密码相关 -----------------------
    password = models.CharField(verbose_name=_("用户密码"), null=True, blank=True, default="", max_length=255)
    password_valid_days = models.IntegerField(
        verbose_name=_("密码有效期"),
        choices=PasswdValidityPeriodEnum.get_choices(),
        default=PasswdValidityPeriodEnum.UNLIMITED.value,  # type: ignore
    )
    password_update_time = models.DateTimeField(verbose_name=_("密码最后更新时间"), null=True, blank=True)
    # ----------------------- 密码相关 -----------------------

    # ----------------------- 职位相关 -----------------------
    position = models.IntegerField(verbose_name=_("职务"), null=True, blank=True, default=0)
    leader = models.ManyToManyField(
        "self",
        blank=True,
        related_name="subordinate_staff",
        verbose_name=_("上级"),
        symmetrical=False,
    )
    # ----------------------- 职位相关 -----------------------

    # ----------------------- 国际化相关 -----------------------
    time_zone = models.CharField(
        verbose_name=_("时区"),
        choices=TIME_ZONE_CHOICES,
        default="Asia/Shanghai",
        max_length=32,
    )
    language = models.CharField(
        verbose_name=_("语言"),
        choices=LanguageEnum.get_choices(),
        default=LanguageEnum.ZH_CN.value,  # type: ignore
        max_length=32,
    )
    # 国际号码段
    country_code = models.CharField(verbose_name=_("国际号码段"), default="86", null=True, blank=True, max_length=32)
    iso_code = models.CharField(verbose_name=_("国家代号"), default="CN", null=True, blank=True, max_length=32)
    # ----------------------- 国际化相关 -----------------------

    # ----------------------- 其他 -----------------------
    extras = jsonfield.JSONField(verbose_name=_("自定义字段"), default={})
    # 虽然 enabled 将被大量用于过滤，但是依旧不应该添加 index,
    # https://stackoverflow.com/questions/10524651/is-there-any-performance-gain-in-indexing-a-boolean-field
    enabled = models.BooleanField(verbose_name=_("是否启用"), default=True)
    # ----------------------- 其他 -----------------------

    # ----------------------- 废弃兼容字段 -----------------------
    type = models.CharField(verbose_name=_("用户类型"), null=True, blank=True, default="", max_length=255)
    role = models.IntegerField(
        verbose_name=_("角色"), choices=RoleCodeEnum.get_choices(), default=RoleCodeEnum.STAFF.value  # type: ignore
    )
    # ----------------------- 废弃兼容字段 -----------------------

    objects = ProfileManager()
    all_objects = ProfileAllManager()
    update_objects = BulkUpdateManager()

    def __str__(self):
        return f"{self.pk}-{self.username}-{self.status}"

    class Meta:
        ordering = ["id"]
        verbose_name = "用户信息"
        verbose_name_plural = "用户信息"
        unique_together = ("username", "category_id")

    def custom_validate(self):
        validate_domain(self.domain)
        validate_username(self.username)
        validate_extras_value_unique(value=self.extras, category_id=self.category_id, profile_id=self.pk)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.custom_validate()
        super().save(force_insert, force_update, using, update_fields)

    def to_audit_info(self):
        """提供审计元信息"""
        return AuditObjMetaInfo(
            key=self.username,
            display_name=self.display_name,
            category_id=self.category_id,
        )

    @property
    def bad_check_cnt(self) -> int:
        return self.login_set.latest_failed_count()

    @property
    def latest_check_time(self):
        return (
            self.login_set.filter(is_success=False, reason=LogInFailReasonEnum.BAD_PASSWORD.value).latest().create_time
        )

    @property
    def is_superuser(self) -> bool:
        return self.role == RoleCodeEnum.SUPERUSER.value  # type: ignore

    @property
    def latest_password_update_time(self) -> datetime.datetime:
        """最近一次更新密码时间"""
        return self.password_update_time or self.create_time

    def enable(self):
        self.enabled = True
        self.status = ProfileStatus.NORMAL.value
        self.save(update_fields=["enabled", "status", "update_time"])

    def delete(self, using=None, keep_parents=False):
        """软删除"""
        self.enabled = False
        self.status = ProfileStatus.DELETED.value

        # 解除与其他模型的绑定关系
        self.departments.clear()
        self.leader.clear()

        self.save(update_fields=["enabled", "status", "update_time"])
        return

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save(update_fields=["password"])

    def check_password(self, raw_password) -> bool:
        """探测密码是否被加密"""
        # 兼容未加密版本
        if not self.password.startswith("pbkdf2_sha256"):
            return self.password == raw_password

        return check_password(raw_password, self.password)


LeaderThroughModel = Profile.leader.through


class DynamicFieldInfo(TimestampedModel):
    """动态字段元信息"""

    name = models.CharField(verbose_name="字段 Key", max_length=32, unique=True)
    display_name = models.CharField(verbose_name="字段名", max_length=64, unique=True)
    type = models.CharField(choices=DynamicFieldTypeEnum.get_choices(), max_length=32)
    require = models.BooleanField(default=False)
    unique = models.BooleanField(default=False)
    # 用户是否能够编辑
    editable = models.BooleanField(default=True)
    # 管理员是否能够编辑
    configurable = models.BooleanField(default=True)
    builtin = models.BooleanField(default=False)
    order = models.IntegerField(verbose_name="顺序")
    # 默认值长度需要考虑
    default = jsonfield.JSONField(verbose_name="默认值", default="")
    enabled = models.BooleanField(verbose_name="是否启用", default=True)
    options = jsonfield.JSONField(verbose_name="选项", default={})
    visible = models.BooleanField(verbose_name="是否展示", default=False)
    map_method = models.CharField(
        verbose_name="值映射方法",
        choices=FieldMapMethod.get_choices(),
        default=FieldMapMethod.DIRECT.value,
        max_length=64,
    )

    objects = DynamicFieldInfoManager()

    class Meta:
        ordering = ["order"]

    def save(self, *args, **kwargs):
        validate_dynamic_field_name(self.name)
        super().save()

    def get_option_key_by_value(self, value: str):
        if not self.options:
            return None

        for value_pair in self.options:
            if value_pair[1] == value:
                return value_pair[0]

    def to_audit_info(self):
        """提供审计元信息"""
        return AuditObjMetaInfo(
            key=self.name,
            display_name=self.display_name,
        )


class ProfileTokenHolder(TimestampedModel):
    """用户 Token"""

    token = models.CharField("用户 Token", max_length=128)
    profile = models.ForeignKey("Profile", related_name="tokens", on_delete=models.CASCADE)
    enabled = models.BooleanField("是否启用", default=True)
    expire_time = models.DateTimeField("过期时间")

    objects = ProfileTokenManager()

    @property
    def expired(self):
        """是否过期"""
        return now() > self.expire_time
