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
import Vue from 'vue';
import axios from 'axios';
import cookie from 'cookie';
import CachedPromise from './cached-promise';
import RequestQueue from './request-queue';
import { messageError } from '@/common/bkmagic';
import store from '@/store';
// import UrlParse from 'url-parse';
// import { parse } from 'query-string';
// axios 实例
const axiosInstance = axios.create({
  withCredentials: true,
  headers: { 'X-Requested-With': 'XMLHttpRequest' },
  xsrfCookieName: 'bkuser_csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  baseURL: window.AJAX_URL,
});

/**
 * request interceptor
 */
// axiosInstance.interceptors.request.use((config) => {
//   const urlObj = new UrlParse(config.url); // { query: '?q=1' }
//   const query = parse(urlObj.query); // { q: '1' }
//   if (query['mock-file']) {
//     if (!urlObj.pathname) {
//       config.url = `http://localhost:8089/mock/${urlObj.query}`;
//     } else if (urlObj.pathname === '/') {
//       config.url = `http://localhost:8089/mock/${urlObj.query}`;
//     } else {
//       config.url = `http://localhost:8089${urlObj.pathname}${urlObj.query}`;
//     }
//   }
//   return config;
// }, error => Promise.reject(error));

/**
 * response interceptor
 */
axiosInstance.interceptors.response.use(
  response => response.data,
  error => Promise.reject(error),
);

const http = {
  queue: new RequestQueue(),
  cache: new CachedPromise(),
  cancelRequest: (requestId) => {
    return http.queue.cancel(requestId);
  },
  cancelCache: requestId => http.cache.delete(requestId),
  cancel: requestId => Promise.all([http.cancelRequest(requestId), http.cancelCache(requestId)]),
};

const methodsWithoutData = ['delete', 'get', 'head', 'options'];
const methodsWithData = ['post', 'put', 'patch'];
const allMethods = [...methodsWithoutData, ...methodsWithData];

// 在自定义对象 http 上添加各请求方法
allMethods.forEach((method) => {
  Object.defineProperty(http, method, {
    get() {
      return getRequest(method);
    },
  });
});

/**
 * 获取 http 不同请求方式对应的函数
 *
 * @param {string} http method 与 axios 实例中的 method 保持一致
 *
 * @return {Function} 实际调用的请求函数
 */
function getRequest(method) {
  if (methodsWithData.includes(method)) {
    return (url, data, config) => getPromise(method, url, data, config);
  }
  return (url, config) => getPromise(method, url, null, config);
}

/**
 * 实际发起 http 请求的函数，根据配置调用缓存的 promise 或者发起新的请求
 *
 * @param {method} http method 与 axios 实例中的 method 保持一致
 * @param {string} 请求地址
 * @param {Object} 需要传递的数据, 仅 post/put/patch 三种请求方式可用
 * @param {Object} 用户配置，包含 axios 的配置与本系统自定义配置
 *
 * @return {Promise} 本次http请求的Promise
 */
async function getPromise(method, url, data, userConfig = {}) {
  const config = initConfig(method, url, userConfig);
  let promise;
  if (config.cancelPrevious) {
    await http.cancel(config.requestId);
  }

  if (config.clearCache) {
    http.cache.delete(config.requestId);
  } else {
    promise = http.cache.get(config.requestId);
  }

  if (config.fromCache && promise) {
    return promise;
  }

  promise = new Promise(async (resolve, reject) => {
    const axiosRequest = methodsWithData.includes(method)
      ? axiosInstance[method](url, data, config)
      : axiosInstance[method](url, config);

    try {
      const response = await axiosRequest;
      Object.assign(config, response.config || {});
      handleResponse({ config, response, resolve, reject });
    } catch (error) {
      Object.assign(config, error.config);
      reject(error);
    }
  }).catch((error) => {
    return handleReject(error, config);
  });

  // 添加请求队列
  http.queue.set(config);
  // 添加请求缓存
  http.cache.set(config.requestId, promise);

  return promise;
}

/**
 * 处理 http 请求成功结果
 *
 * @param {Object} 请求配置
 * @param {Object} cgi 原始返回数据
 * @param {Function} promise 完成函数
 * @param {Function} promise 拒绝函数
 */
function handleResponse({ config, response, resolve, reject }) {
  const { message } = response;
  if (response.result) {
    // 通过 result 判断请求是否正确
    resolve(config.originalResponse ? response : response.data, config);
  } else {
    reject({
      message,
      info: `${config.requestId} response.result ${response.result}`,
    });
    if (config.globalError) {
      message && messageError(message);
    }
  }
  http.queue.delete(config.requestId);
}

/**
 * 处理 http 请求失败结果
 *
 * @param {Object} Error 对象
 * @param {config} 请求配置
 *
 * @return {Promise} promise 对象
 */

function handleReject(error, config) {
  if (axios.isCancel(error)) {
    return Promise.reject(error);
  }
  http.queue.delete(config.requestId);

  if (config.globalError && error.response) {
    console.warn('errorMessage', error.message);
    console.warn('errorResponse', error.response);

    // 请求出错了，统一处理
    const { status, data } = error.response;
    if (status === 401) {
      try {
        const { login_url: loginUrl, extra_params: extraParams } = data;
        let extraQuery = '';
        extraParams && Object.entries(extraParams).forEach((arr) => {
          extraQuery += (`&${arr[0]}=${arr[1]}`);
        });

        if (!loginUrl.includes(window.origin)) { // 登录弹窗 iframe 跨域，跳转登录
          const url = `${loginUrl}?c_url=${window.location}${extraQuery}`;
          window.location.assign(url);
        } else { // 弹窗登录
          const callbackUrl = `${window.origin + window.SITE_URL}accounts/login_success/`;
          const url = `${loginUrl}?c_url=${callbackUrl}${extraQuery}`;
          window.bus.$emit('show-login-modal', Object.assign(data, {
            loginUrl: url,
          }));
        }
      } catch (e) {
        console.warn('登录401响应数据结构错误', e);
      }
    } else if (status === 403 && data.code === -1) {
      store.commit('updateNoAuthData', {
        requestId: config.requestId,
        data,
      });
    } else if (status === 403 && data.code === -2) {
      store.commit('updateNoAccessAuthData', data.message);
      store.commit('updateInitLoading', false);
    } else if (data && data.message) {
      messageError(data.message);
    } else if (status === 500) {
      messageError('系统出现异常');
    } else {
      messageError(error.message);
    }
  }
  return Promise.reject(error);
}

/**
 * 初始化本系统 http 请求的各项配置
 *
 * @param {string} http method 与 axios 实例中的 method 保持一致
 * @param {string} 请求地址, 结合 method 生成 requestId
 * @param {Object} 用户配置，包含 axios 的配置与本系统自定义配置
 *
 * @return {Promise} 本次 http 请求的 Promise
 */
function initConfig(method, url, userConfig) {
  const defaultConfig = {
    ...getCancelToken(),
    // http 请求默认 id
    requestId: `${method}_${url}`,
    // 是否全局捕获异常
    globalError: true,
    // 是否直接复用缓存的请求
    fromCache: false,
    // 是否在请求发起前清楚缓存
    clearCache: false,
    // 响应结果是否返回原始数据
    originalResponse: true,
    // 当路由变更时取消请求
    cancelWhenRouteChange: true,
    // 取消上次请求
    cancelPrevious: true,
  };
  return Object.assign(defaultConfig, userConfig);
}

/**
 * 生成 http 请求的 cancelToken，用于取消尚未完成的请求
 *
 * @return {Object} {cancelToken: axios 实例使用的 cancelToken, cancelExcutor: 取消http请求的可执行函数}
 */
function getCancelToken() {
  let cancelExcutor;
  const cancelToken = new axios.CancelToken((excutor) => {
    cancelExcutor = excutor;
  });
  return {
    cancelToken,
    cancelExcutor,
  };
}

Vue.prototype.$http = http;

export default http;

/**
 * 向 http header 注入 CSRFToken，CSRFToken key 值与后端一起协商制定
 */
export function injectCSRFTokenToHeaders() {
  const CSRFToken = cookie.parse(document.cookie).bkuser_csrftoken;
  if (CSRFToken !== undefined) {
    axiosInstance.defaults.headers.common['X-CSRFToken'] = CSRFToken;
  } else {
    console.warn('Can not find bkuser_csrftoken in document.cookie');
  }
}
