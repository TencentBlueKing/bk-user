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
import logging
from typing import List

from django.utils import timezone

from bkuser.apps.data_source.models import DataSource, DataSourceUser, LocalDataSourceIdentityInfo
from bkuser.common.constants import PERMANENT_TIME
from bkuser.common.passwd import PasswordGenerator
from bkuser.plugins.local.constants import PasswordGenerateMethod
from bkuser.plugins.local.models import LocalDataSourcePluginConfig, PasswordInitialConfig, PasswordRuleConfig

logger = logging.getLogger(__name__)


class PasswordProvider:
    """本地数据源用户密码"""

    def __init__(self, passwd_rule_cfg: PasswordRuleConfig, passwd_initial_cfg: PasswordInitialConfig):
        self.generate_method = passwd_initial_cfg.generate_method
        self.fixed_password = passwd_initial_cfg.fixed_password
        self.passwd_generator = PasswordGenerator(passwd_rule_cfg.to_rule())

    def generate(self) -> str:
        if self.generate_method == PasswordGenerateMethod.FIXED and self.fixed_password:
            return self.fixed_password

        return self.passwd_generator.generate()


class LocalDataSourceIdentityInfoInitializer:
    """本地数据源用户身份数据初始化"""

    BATCH_SIZE = 250

    def __init__(self, data_source: DataSource):
        self.data_source = data_source
        if not data_source.is_local:
            return

        self.plugin_cfg = LocalDataSourcePluginConfig(**data_source.plugin_config)
        if not self.plugin_cfg.enable_account_password_login:
            return

        self.password_provider = PasswordProvider(
            self.plugin_cfg.password_rule, self.plugin_cfg.password_initial  # type: ignore
        )

    def sync(self) -> List[DataSourceUser]:
        """检查指定数据源的所有用户，对没有账密信息的，做初始化，适用于批量同步（导入）的情况"""
        if self._can_skip():
            return []

        exists_info_user_ids = LocalDataSourceIdentityInfo.objects.filter(
            data_source=self.data_source,
        ).values_list("user_id", flat=True)
        # NOTE：已经存在的账密信息，不会按照最新规则重新生成！不然用户密码就失效了！
        waiting_init_users = DataSourceUser.objects.filter(
            data_source=self.data_source,
        ).exclude(id__in=exists_info_user_ids)

        self._init_users_identity_info(waiting_init_users)
        return waiting_init_users

    def initialize(self, user: DataSourceUser) -> None:
        """初始化用户身份信息，适用于单个用户创建的情况"""
        if self._can_skip():
            return

        if LocalDataSourceIdentityInfo.objects.filter(user=user).exists():
            logger.warning("local data source user %s identity info exists, skip initialize", user.id)
            return

        self._init_users_identity_info([user])

    def _can_skip(self) -> bool:
        """预先判断能否直接跳过"""

        # 不是本地数据源的，不需要初始化
        if not self.data_source.is_local:
            return True

        # 是本地数据源，但是没开启账密登录的，不需要初始化
        if not self.plugin_cfg.enable_account_password_login:
            return True

        return False

    def _init_users_identity_info(self, users: List[DataSourceUser]):
        """初始化用户身份信息"""
        time_now = timezone.now()
        expired_at = self._get_password_expired_at()

        waiting_create_infos = [
            LocalDataSourceIdentityInfo(
                user=user,
                password=self.password_provider.generate(),
                password_updated_at=time_now,
                password_expired_at=expired_at,
                data_source=self.data_source,
                username=user.username,
            )
            for user in users
        ]
        LocalDataSourceIdentityInfo.objects.bulk_create(waiting_create_infos, batch_size=self.BATCH_SIZE)

    def _get_password_expired_at(self) -> datetime.datetime:
        """获取密码过期的具体时间"""
        valid_time: int = self.plugin_cfg.password_rule.valid_time  # type: ignore
        # 有效时间 -1 表示永远有效
        if valid_time < 0:
            return PERMANENT_TIME

        return timezone.now() + datetime.timedelta(days=valid_time)
