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
/* eslint-disable no-unused-vars */
import http from '@/api';

export default {
  namespaced: true,
  state: {},
  mutations: {},
  actions: {
    // 判断token是否过期
    getToken(context, params, config = {}) {
      return http.get(`api/v1/password/check_token/?token=${params}`);
    },
    // 设置新密码
    setByToken(context, params, config = {}) {
      return http.post('api/v1/web/passwords/reset/by_token/', params);
    },
    // 修改密码
    modify(context, params, config = {}) {
      return http.post('api/v1/web/passwords/modify/', params);
    },
    // 邮箱重置密码
    reset(context, params, config = {}) {
      return http.post('api/v1/web/passwords/reset/send_email/', params);
    },
    // 获取短信验证码
    sendSms(context, params, config = {}) {
      return http.post('api/v1/web/passwords/reset/verification_code/send_sms/', params);
    },
    // 发送验证码
    sendCode(context, params, config = {}) {
      return http.post('api/v1/web/passwords/reset/verification_code/verify/', params);
    },
    // 获取rsa公钥
    getRsa(context, params, config = {}) {
      return http.get(`api/v1/web/passwords/settings/by_token/?token=${params}`);
    },
  },
};
