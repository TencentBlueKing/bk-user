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
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

from bkuser.apps.data_source.models import DataSourcePlugin
from bkuser.plugins.constants import CUSTOM_PLUGIN_ID_PREFIX, MAX_LOGO_SIZE
from bkuser.utils.base64 import load_image_as_base64


class Command(BaseCommand):
    """向数据库中写入数据源插件信息"""

    def add_arguments(self, parser):
        parser.add_argument("--dir_name", dest="dir_name", required=True, help="插件目录名称")

    def handle(self, dir_name, *args, **options):
        plugin_base_dir = settings.BASE_DIR / "bkuser" / "plugins"
        # 1. 检查指定的插件目录是否存在
        if not os.path.isdir(plugin_base_dir / dir_name):
            raise RuntimeError(f"plugin directory [{dir_name}] not found in bkuser/plugins!")

        # 2. 检查自定义插件是否配置 Metadata
        try:
            metadata = import_string(f"bkuser.plugins.{dir_name}.METADATA")
        except ImportError:
            raise RuntimeError("custom data source plugin must set metadata!")

        # 3. 确保自定义插件的 ID 符合规范
        if not metadata.id.startswith(CUSTOM_PLUGIN_ID_PREFIX):
            raise RuntimeError(f"custom plugin's id must start with `{CUSTOM_PLUGIN_ID_PREFIX}`")

        logo_path = plugin_base_dir / f"{dir_name}/logo.png"

        # 4. 如果发现有 logo，还需要检查下尺寸大小，避免有性能问题
        if os.path.exists(logo_path) and os.path.getsize(logo_path) > MAX_LOGO_SIZE:
            raise RuntimeError(f"plugin logo size must be less than {MAX_LOGO_SIZE/1024}KB!")

        # 5. 尝试获取下 logo，取不到就用默认的
        try:
            logo = load_image_as_base64(logo_path)
        except Exception:
            self.stdout.write("failed to load plugin logo, use default logo...")
            logo = ""

        # 6. 如果同名插件已存在，更新，否则创建
        DataSourcePlugin.objects.update_or_create(
            id=metadata.id,
            defaults={
                "name": metadata.name,
                "description": metadata.description,
                "logo": logo,
            },
        )

        # 7. 注册到 DB 成功要给提示
        self.stdout.write(f"register data source plugin [{metadata.id}] into database successfully.")
