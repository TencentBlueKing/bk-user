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
import hashlib
import logging

from django.contrib.auth.hashers import make_password
from django.utils.encoding import force_bytes

from bkuser.apps.data_source.constants import DataSourceType
from bkuser.apps.data_source.models import DataSourcePlugin, DataSource, DataSourceUser
from bkuser.biz.utils import gen_random_str

logger = logging.getLogger(__name__)


class DataSourceHandler:
    def _make_password_by_config(self, config, return_raw=False):
        if config["init_password_method"] == "fixed_preset":
            raw_password = config["init_password"]
        else:
            raw_password = gen_random_str(12)
        if return_raw:
            return raw_password

        return make_password(raw_password)

    def _get_code(self, name, owner) -> str:
        """通过对象 dn 生成 唯一code"""
        tmp_str = f"{name}-{owner}"
        sha = hashlib.sha256(force_bytes(tmp_str)).hexdigest()
        logger.info("use data_source_name and owner to be code: %s -> %s", tmp_str, sha)
        return sha

    def create_data_source(self, name, owner, data_source_type=DataSourceType.LOCAL.value):
        local_data_source_plugin = DataSourcePlugin.objects.get(type=data_source_type)
        code = self._get_code(name, owner)
        data_source = DataSource.objects.create(
            name=name,
            code=code,
            owner=owner,
            plugin_id=local_data_source_plugin.id,
            plugin_config=local_data_source_plugin.config_meta,
        )
        return data_source

    def create_data_source_users(self, instance: DataSource, users):
        data_source_users = []
        password_config = instance.plugin_config["password"]
        for user in users:
            user["password"] = self._make_password_by_config(password_config)
            data_source_users.append(DataSourceUser(data_source_id=instance.id, **user))
        DataSourceUser.objects.bulk_create(data_source_users)
        return [user["username"] for user in users]

    def update_plugin_config(self, instance, update_data: dict, namespace: str):
        plugin_config = instance.plugin_config
        config = plugin_config.get(namespace, {})

        if not config:
            logger.error(f"plugin config has no this config. namespace:{namespace}")

        for key, value in update_data.items():
            config[key] = value
        plugin_config[namespace] = config
        instance.save()
        return instance


data_source_handler = DataSourceHandler()
