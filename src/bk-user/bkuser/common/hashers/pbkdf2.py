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
from typing import Dict

from django.contrib.auth.hashers import BasePasswordHasher, mask_hash, must_update_salt
from django.utils.crypto import constant_time_compare
from django.utils.encoding import force_bytes

from .sm3 import SM3


def _pbkdf2_hmac_sm3(password: bytes, salt: bytes, iterations: int, dk_len: int | None = None) -> bytes:
    """
    Password based key derivation function 2 (PKCS #5 v2.0)
    实现参考自：lib/python3.10/hashlib.py L188 pbkdf2_hmac

    TODO 性能优化，目前相同迭代次数条件下，pbkdf2_sm3_hmac 性能仅为 pbkdf2_hmac + sha256 的 1/70
    原因有二：1. tongsuopy.SM3 性能约为 hashlib.sha256 的 1/15
            2. 本函数 pbkdf2_hmac 实现性能约为标准库 pbkdf2_hmac 的 1/4
            注：标准库 pbkdf2_hmac 为 C 实现且带缓存，但仅支持 hashlib 内置的算法（如 sha1, sha256）
    """
    inner, outer = SM3(), SM3()
    block_size = inner.block_size

    if iterations < 1:
        raise ValueError("pbkdf2 iterations must greater than 0")
    if dk_len is None:
        dk_len = outer.digest_size
    if dk_len < 1:
        raise ValueError("pbkdf2 dklen must greater than 0")

    if len(password) > block_size:
        password = SM3(password).digest()

    password = password + b"\x00" * (block_size - len(password))

    _trans_5C = bytes((x ^ 0x5C) for x in range(256))  # noqa: N806
    _trans_36 = bytes((x ^ 0x36) for x in range(256))
    inner.update(password.translate(_trans_36))
    outer.update(password.translate(_trans_5C))

    def prf(msg):
        # PBKDF2_HMAC uses the password as key. We can re-use the same
        # digest objects and just update copies to skip initialization.
        inner_cp = inner.copy()
        outer_cp = outer.copy()
        inner_cp.update(msg)
        outer_cp.update(inner_cp.digest())
        return outer_cp.digest()

    d_key = b""
    loop = 1
    while len(d_key) < dk_len:
        prev = prf(salt + loop.to_bytes(4, "big"))
        r_key = int.from_bytes(prev, "big")
        for _i in range(iterations - 1):
            prev = prf(prev)
            # r_key = r_key ^ prev
            r_key ^= int.from_bytes(prev, "big")

        loop += 1
        d_key += r_key.to_bytes(inner.digest_size, "big")

    return d_key[:dk_len]


class PBKDF2SM3PasswordHasher(BasePasswordHasher):
    """
    Secure password hashing using the PBKDF2 algorithm

    Configured to use PBKDF2 + HMAC + SM3.
    """

    algorithm = "pbkdf2_sm3"
    # PBKDF2PasswordHasher 迭代次数为 26w，由于 _pbkdf2_hmac_sm3 性能仅为 pbkdf2_hmac + sha256 的 1/70
    # 因此此处设置迭代次数为 2.6w, 综上可得本 Hasher 性能约为 PBKDF2PasswordHasher 的 1/6 - 1/7
    iterations = 26000

    def encode(self, password: str, salt: str | None = None, iterations: int | None = None) -> str:
        """根据指定的原始密码，盐值，迭代次数生成加密信息"""
        salt = salt or self.salt()
        iterations = iterations or self.iterations
        hash_bytes = _pbkdf2_hmac_sm3(force_bytes(password), force_bytes(salt), iterations)
        hash = base64.b64encode(hash_bytes).decode("ascii").strip()
        return "%s$%d$%s$%s" % (self.algorithm, iterations, salt, hash)

    def decode(self, encoded: str) -> Dict:
        """将加密信息各部分拆分返回"""
        algorithm, iterations, salt, hash = encoded.split("$", 3)
        assert algorithm == self.algorithm
        return {
            "algorithm": algorithm,
            "hash": hash,
            "iterations": int(iterations),
            "salt": salt,
        }

    def verify(self, password: str, encoded: str) -> bool:
        """校验密码是否正确"""
        decoded = self.decode(encoded)
        re_encoded = self.encode(password, decoded["salt"], decoded["iterations"])
        # 使用 constant_time_compare 而非直接比较，可以避免时序分析攻击
        return constant_time_compare(encoded, re_encoded)

    def safe_summary(self, encoded: str) -> Dict:
        """将加密信息各部分拆分返回（含 Mask）"""
        decoded = self.decode(encoded)
        return {
            "algorithm": decoded["algorithm"],
            "iterations": decoded["iterations"],
            "salt": mask_hash(decoded["salt"]),
            "hash": mask_hash(decoded["hash"]),
        }

    def must_update(self, encoded: str) -> bool:
        """根据盐长度是否符合预期，以及当前加密信息的迭代次数，判断是否增加迭代次数（空转）"""
        decoded = self.decode(encoded)
        update_salt = must_update_salt(decoded["salt"], self.salt_entropy)
        return (decoded["iterations"] != self.iterations) or update_salt

    def harden_runtime(self, password: str, encoded: str) -> None:
        """空转，以确保与当前 hasher 迭代次数不一致/盐值长度不同的密码信息，验证时间均基本一致"""
        decoded = self.decode(encoded)
        extra_iterations = self.iterations - decoded["iterations"]
        if extra_iterations > 0:
            self.encode(password, decoded["salt"], extra_iterations)
