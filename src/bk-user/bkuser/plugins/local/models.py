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
from typing import List, Optional

from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel, Field, ValidationError, model_validator

from bkuser.common.passwd import PasswordGenerateError, PasswordGenerator, PasswordRule, PasswordValidator
from bkuser.plugins.local.constants import (
    MAX_LOCK_TIME,
    MAX_NOT_CONTINUOUS_COUNT,
    MAX_PASSWORD_LENGTH,
    MAX_PASSWORD_VALID_TIME,
    MAX_RESERVED_PREVIOUS_PASSWORD_COUNT,
    NEVER_EXPIRE_TIME,
    PASSWORD_MAX_RETRIES,
    NotificationMethod,
    NotificationScene,
    PasswordGenerateMethod,
)
from bkuser.plugins.models import BasePluginConfig
from bkuser.utils.pydantic import stringify_pydantic_error


class PasswordRuleConfig(BaseModel):
    """密码规则配置"""

    # 密码最小长度
    min_length: int = Field(le=MAX_PASSWORD_LENGTH)

    # --- 字符限制类 ---
    # 必须包含小写字母
    contain_lowercase: bool
    # 必须包含大写字母
    contain_uppercase: bool
    # 必须包含数字
    contain_digit: bool
    # 必须包含特殊字符（标点符号）
    contain_punctuation: bool

    # --- 连续性限制类 ---
    # 不允许连续出现位数
    not_continuous_count: int = Field(default=0, ge=0, le=MAX_NOT_CONTINUOUS_COUNT)
    # 不允许键盘序
    not_keyboard_order: bool
    # 不允许连续字母序
    not_continuous_letter: bool
    # 不允许连续数字序
    not_continuous_digit: bool
    # 不允许重复字母，数字，特殊字符
    not_repeated_symbol: bool

    # 密码有效期（单位：天）
    valid_time: int = Field(ge=NEVER_EXPIRE_TIME, le=MAX_PASSWORD_VALID_TIME)
    # 密码试错次数
    max_retries: int = Field(ge=0, le=PASSWORD_MAX_RETRIES)
    # 锁定时间（单位：秒）
    lock_time: int = Field(ge=NEVER_EXPIRE_TIME, le=MAX_LOCK_TIME)

    def to_rule(self) -> PasswordRule:
        """转换成密码工具可用的规则"""
        return PasswordRule(
            # 长度
            min_length=self.min_length,
            max_length=MAX_PASSWORD_LENGTH,
            # 字符集
            contain_lowercase=self.contain_lowercase,
            contain_uppercase=self.contain_uppercase,
            contain_digit=self.contain_digit,
            contain_punctuation=self.contain_punctuation,
            # 连续性
            not_continuous_count=self.not_continuous_count,
            not_keyboard_order=self.not_keyboard_order,
            not_continuous_letter=self.not_continuous_letter,
            not_continuous_digit=self.not_continuous_digit,
            not_repeated_symbol=self.not_repeated_symbol,
        )


class NotificationTemplate(BaseModel):
    """通知模板"""

    # 通知方式 如短信，邮件
    method: NotificationMethod
    # 通知场景 如将过期，已过期
    scene: NotificationScene
    # 模板标题
    title: Optional[str] = None
    # 模板发送方
    sender: str
    # 模板内容（text）格式
    content: str
    # 模板内容（html）格式
    content_html: str

    @model_validator(mode="after")
    def validate_attrs(self) -> "NotificationTemplate":
        if self.method == NotificationMethod.EMAIL and not self.title:
            raise ValueError(_("邮件通知模板需要提供标题"))

        return self


class NotificationConfig(BaseModel):
    """通知相关配置"""

    enabled_methods: List[NotificationMethod]
    # 通知模板
    templates: List[NotificationTemplate]


class PasswordInitialConfig(BaseModel):
    """初始密码设置"""

    # 首次登录后强制修改密码
    force_change_at_first_login: bool
    # 修改密码时候不能使用之前的密码
    cannot_use_previous_password: bool
    # 之前的 N 个密码不能被本次修改使用，仅当 cannot_use_previous_password 为 True 时有效
    reserved_previous_password_count: int = Field(default=0, ge=0, le=MAX_RESERVED_PREVIOUS_PASSWORD_COUNT)
    # 初始密码生成方式
    generate_method: PasswordGenerateMethod
    # 固定初始密码（仅密码生成方式为'固定值'时有效）
    # FIXME (su) 固定的初始密码需要加密存储，考虑独立建表？且因为需要在通知时使用，只能使用对称加密？
    fixed_password: Optional[str] = None
    # 通知相关配置
    notification: NotificationConfig


class PasswordExpireConfig(BaseModel):
    """密码到期相关配置"""

    # 在密码到期多久前提醒，单位：天，多个值表示多次提醒
    remind_before_expire: List[int]
    # 通知相关配置
    notification: NotificationConfig


class LocalDataSourcePluginConfig(BasePluginConfig):
    """本地数据源插件配置"""

    # 敏感字段
    sensitive_fields = [
        "password_initial.fixed_password",
    ]

    # 是否允许使用账密登录
    enable_account_password_login: bool
    # 密码生成规则
    password_rule: Optional[PasswordRuleConfig] = None
    # 密码初始化/修改规则
    password_initial: Optional[PasswordInitialConfig] = None
    # 密码到期规则
    password_expire: Optional[PasswordExpireConfig] = None

    @model_validator(mode="after")
    def validate_attrs(self) -> "LocalDataSourcePluginConfig":
        """插件配置合法性检查"""
        # 如果没有开启账密登录，则不需要检查配置
        if not self.enable_account_password_login:
            return self

        # 若启用账密登录，则各字段都需要配置上
        if not (self.password_rule and self.password_initial and self.password_expire):
            raise ValueError(_("密码生成规则、初始密码设置、密码到期设置均不能为空"))

        try:
            rule = self.password_rule.to_rule()
        except ValidationError as e:
            raise ValueError(_("密码生成规则不合法: {}").format(stringify_pydantic_error(e)))

        if self.password_initial.generate_method == PasswordGenerateMethod.FIXED:
            # 如果初始密码生成模式为固定密码，则需要为固定密码预设值
            if not self.password_initial.fixed_password:
                raise ValueError(_("固定密码不能为空"))

            # 若配置固定密码，则需要检查是否符合定义的密码强度规则
            ret = PasswordValidator(rule).validate(self.password_initial.fixed_password)
            if not ret.ok:
                raise ValueError(_("固定密码的值不符合密码规则：{}").format(ret.exception_message))
        else:
            # 随机生成密码的，校验下能否在有限次数内成功生成
            try:
                PasswordGenerator(rule).generate()
            except PasswordGenerateError:
                raise ValueError(_("无法根据预设规则生成符合条件的密码，请调整规则"))

        return self
