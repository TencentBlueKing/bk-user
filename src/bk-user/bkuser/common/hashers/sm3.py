# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import binascii

from tongsuopy.crypto.hashes import SM3 as TongSuoSM3  # noqa: N811
from tongsuopy.crypto.hashes import Hash


class SM3:
    name = TongSuoSM3.name
    digest_size = TongSuoSM3.digest_size
    block_size = TongSuoSM3.block_size

    def __init__(self, data: bytes | None = None) -> None:
        self.hash = Hash(TongSuoSM3())
        if data:
            self.hash.update(data)

    def copy(self: "SM3") -> "SM3":
        new = SM3()
        new.hash = self.hash.copy()
        return new

    def digest(self) -> bytes:
        return self.hash.finalize()

    def hexdigest(self) -> str:
        digest = self.digest()
        return binascii.hexlify(digest).decode()

    def update(self, data) -> None:
        self.hash.update(data)
