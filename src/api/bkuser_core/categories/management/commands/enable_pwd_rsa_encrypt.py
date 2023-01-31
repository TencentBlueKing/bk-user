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
import base64
import logging
import traceback

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa as crypto_rsa
from django.core.management.base import BaseCommand
from django.db import transaction

from bkuser_core.categories.constants import CategoryType
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.user_settings.models import Setting, SettingMeta

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "enable category rsa"

    def add_arguments(self, parser):
        parser.add_argument("--category_id", type=str, help="目录ID", required=True)
        parser.add_argument("--random_flag", type=bool, default=True, help="是否随机生成")
        parser.add_argument("--key_length", type=int, default=1024, help="随机密钥对的长度")
        parser.add_argument("--private_key_file", type=str, default="", help="rsa私钥pem文件目录")
        parser.add_argument("--public_key_file", type=str, default="", help="rsa公钥pem文件目录")

    def validate_rsa_secret(self, private_key_content: bytes, public_key_content: bytes) -> bool:
        testing_msg = "Hello World !!!"

        private_key = serialization.load_pem_private_key(private_key_content, password=None, backend=default_backend())
        public_key = serialization.load_pem_public_key(public_key_content, backend=default_backend())

        common_condition = padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None
        )

        # 先公钥加密
        encrypt_msg = public_key.encrypt(testing_msg.encode(), common_condition)

        # 解密
        decrypt_msg = private_key.decrypt(encrypt_msg, common_condition)
        result_msg = decrypt_msg.decode()

        if result_msg != testing_msg:
            return False
        return True

    def create_rsa_secret(self, options: dict):
        random_flag = options.get("random_flag")
        private_key: bytes
        public_key: bytes
        if not random_flag:
            # read the private_key and public key from the file
            private_key_file: str = options.get("private_key_file", "")
            public_key_file: str = options.get("public_key_file", "")
            with open(private_key_file, "rb") as private_file:
                private_key = private_file.read()

            with open(public_key_file, "rb") as public_file:
                public_key = public_file.read()

            if not self.validate_rsa_secret(private_key, private_key):
                self.stdout.write("These pem files do not matching")
                raise Exception
        else:
            self.stdout.write("Private key and public key are creating randomly")
            key_length = options.get("key_length")
            # 随机生成rsa 秘钥对
            private_key_origin = crypto_rsa.generate_private_key(
                public_exponent=65537, key_size=key_length, backend=default_backend()
            )
            public_key_origin = private_key_origin.public_key()

            private_key = private_key_origin.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )

            public_key = public_key_origin.public_bytes(
                encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.PKCS1
            )

        # base64加密入库
        public_key_base64: str = base64.b64encode(public_key).decode()
        private_key_base64: str = base64.b64encode(private_key).decode()

        return public_key_base64, private_key_base64

    def handle(self, *args, **options):
        category_id = options.get("category_id")
        self.stdout.write(f"enable category rsa: category_id={str(category_id)}")

        try:
            public_key, private_key = self.create_rsa_secret(options)
            category = ProfileCategory.objects.get(id=category_id)
            if category.type != CategoryType.LOCAL.value:
                self.stdout.write("Rsa setting only support the local category, please check your input")
                return

            rsa_settings_filters = {
                "enable_password_rsa_encrypted": True,
                "password_rsa_private_key": private_key,
                "password_rsa_public_key": public_key,
            }

            meta_combo = {}
            for key, value in rsa_settings_filters.items():
                meta = SettingMeta.objects.get(key=key)
                meta_combo[meta] = value

            # 新增或更新该目录的user_setting设置：rsa配置
            with transaction.atomic():
                rsa_settings = []
                for meta, value in meta_combo.items():
                    instance, _ = Setting.objects.get_or_create(meta=meta, category_id=category.id)
                    instance.value = value
                    rsa_settings.append(instance)
                Setting.objects.bulk_update(rsa_settings, ["value"])

            self.stdout.write(f"Category {category_id} Enable rsa successfully")

        except ProfileCategory.DoesNotExist:
            self.stdout.write(f"Category is not exist( category_id={category_id} ), please check your input.")
            return

        except Exception as e:
            self.stdout.write(traceback.format_exc())
            self.stdout.write(f"Enable rsa failed:  {e}")
            return
