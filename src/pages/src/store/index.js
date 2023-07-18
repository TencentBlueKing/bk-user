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
import Vue from 'vue';
import Vuex from 'vuex';
import http from '@/api';
import i18n from '@/language/i18n';
import organization from '@/store/modules/organization';
import catalog from '@/store/modules/catalog';
import audit from '@/store/modules/audit';
import setting from '@/store/modules/setting';
import password from '@/store/modules/password';
import { unifyObjectStyle } from '@/common/util';
Vue.use(Vuex);
const store = new Vuex.Store({
  modules: {
    organization,
    catalog,
    audit,
    setting,
    password,
  },
  state: {
    // 密码有效期
    passwordValidDaysList: [{
      days: 30,
      text: i18n.t('一个月'),
    }, {
      days: 90,
      text: i18n.t('三个月'),
    }, {
      days: 180,
      text: i18n.t('六个月'),
    }, {
      days: 365,
      text: i18n.t('一年'),
    }, {
      days: -1,
      text: i18n.t('永久'),
    }],
    recycleDaysList: [{
      days: 7,
      text: i18n.t('7天'),
    }, {
      days: 30,
      text: i18n.t('30天'),
    }, {
      days: 90,
      text: i18n.t('90天'),
    }, {
      days: 180,
      text: i18n.t('180天'),
    }, {
      days: 365,
      text: i18n.t('1年'),
    }],
    initLoading: false,
    // 接口返回403，code = -1 的相关数据
    noAuthData: null,
    // 接口返回403，code = -2 的相关数据
    noAccessAuthData: null,
    // 本地默认头像
    localAvatar: 'data:image/png;base64,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',
  },
  getters: {},
  mutations: {
    updateInitLoading(state, payload) {
      state.initLoading = payload;
    },
    updateNoAuthData(state, payload) {
      state.noAuthData = payload;
    },
    updateNoAccessAuthData(state, payload) {
      state.noAccessAuthData = payload;
    },
  },
  actions: {
    // 获取登录用户基本信息：头像、用户名
    getUserInfo(context, params) {
      return http.get('api/v1/web/profiles/me/');
    },
    getVersionLog(context, params) {
      return http.get('api/v1/web/version_logs/');
    },
    getFooter() {
      return http.get('api/v1/web/site/footer/');
    },
  },
});

/**
 * hack vuex dispatch, add third parameter `config` to the dispatch method
 *
 * @param {Object|string} _type vuex type
 * @param {Object} _payload vuex payload
 * @param {Object} config config 参数，主要指 http 的参数，详见 src/api/index initConfig
 *
 * @return {Promise} 执行请求的 promise
 */
store.dispatch = function (_type, _payload, config = {}) {
  const { type, payload } = unifyObjectStyle(_type, _payload);

  const action = { type, payload, config };
  const entry = store._actions[type];
  if (!entry) {
    if (NODE_ENV !== 'production') {
      console.error(`[vuex] unknown action type: ${type}`);
    }
    return;
  }

  store._actionSubscribers.forEach(() => {
    return action, store.state;
  });

  return entry.length > 1
    ? Promise.all(entry.map(handler => handler(payload, config)))
    : entry[0](payload, config);
};

export default store;
