/**
* by making 蓝鲸智云-用户管理(Bk-User) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License");
* you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing,
* software distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and limitations under the License.
*/
/* 数据RSA加密 */
import JSEncrypt from 'jsencrypt';

export default {
  // JSEncrypt 加密
  rsaPublicData(data, publicKey) {
    const jsencrypt = new JSEncrypt();
    jsencrypt.setPublicKey(publicKey);
    const result = jsencrypt.encrypt(data);
    return result;
  },
  // JSEncrypt 解密
  rsaPrivateData(data, privateKey) {
    const jsencrypt = new JSEncrypt();
    jsencrypt.setPrivateKey(privateKey);
    const result = jsencrypt.encrypt(data);
    return result;
  },
};
