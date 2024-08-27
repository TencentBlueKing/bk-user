import axios, { AxiosError, type AxiosRequestConfig, type AxiosResponse } from 'axios';
import { Message } from 'bkui-vue';
import Cookies from 'js-cookie';
import qs from 'query-string';

import { showLoginModal } from '@blueking/login-modal';

import '../../css/index.css';
import { getLoginUrl } from '@/common/auth';

type Methods = 'delete' | 'get' | 'head' | 'options' | 'post' | 'put' | 'patch';

interface ResolveResponseParams<D> {
  response: AxiosResponse<D, any>,
  config: Record<string, any>,
}

interface Config extends AxiosRequestConfig {
  globalError?: boolean
}
interface ServiceResponseData<T> {
  code: number,
  message: string,
  request_id: string,
  data: T
}

type HttpMethod = <T>(url: string, payload?: any, useConfig?: Config) => Promise<T>;

interface Http {
  get: HttpMethod;
  post: HttpMethod;
  put: HttpMethod;
  delete: HttpMethod;
  head: HttpMethod;
  options: HttpMethod;
  patch: HttpMethod;
}

const baseURL = /http(s)?:\/\//.test(window.AJAX_BASE_URL)
  ? window.AJAX_BASE_URL
  : location.origin + window.AJAX_BASE_URL;

const axiosInstance = axios.create({
  baseURL,
  withCredentials: true,
  xsrfCookieName: window.CSRF_COOKIE_NAME,
  xsrfHeaderName: 'X-CSRFToken',
  headers: {
    'x-requested-with': 'XMLHttpRequest',
  },
});

// 添加请求拦截
axiosInstance.interceptors.request.use(config => config, error => Promise.reject(error));

// 添加响应拦截
axiosInstance.interceptors.response.use(response => response, error => Promise.reject(error));

const methodsWithoutData = ['delete', 'get', 'head', 'options'];
const methodsWithData = ['post', 'put', 'patch'];
const methods = [...methodsWithoutData, ...methodsWithData];

const http = {};

const initConfig = (useConfig: Config) => {
  const baseConfig = {
    globalError: true,
  };
  return Object.assign(baseConfig, useConfig) as Config;
};

const getFetchURL = (url: string, method: string, payload: any) => {
  if (methodsWithData.includes(method)) return url;

  const params = qs.stringify(payload);
  return params ? `${url}?${params}` : url;
};

const handleResponse = <T>({
  response,
}: ResolveResponseParams<ServiceResponseData<T>>) => {
  const { data } = response;
  return Promise.resolve(data);
};

const handleReject = (error: AxiosError, config: Record<string, any>) => {
  const { status } = error.response;
  const { message = '', data = {}, code = '', details = [] } = error.response.data.error;

  if (status === 401) {
    if (error.config.url === '/api/v3/web/basic/current-user/') {
      return window.location.href = getLoginUrl(false);
    }
    // 登录弹窗
    const loginUrl = getLoginUrl();
    showLoginModal({
      loginUrl,
      width: data.width,
      height: data.height,
    });

    return;
  }

  // 全局捕获错误给出提示
  if (config.globalError) {
    details[0].message = JSON.parse(details[0].message);
    const config = {
      overview: '',
      code,
      suggestion: message,
      details: details[0],
    };
    Message({
      theme: 'error',
      message: config,
      delay: 10000,
      extCls: 'message-fix-fixed',
      actions: [
        {
          id: 'assistant',
          disabled: true,
        },
      ] });
  }

  return Promise.reject(error);
};

// 更新axios实例的cookie
function updateAxiosInstance() {
  const csrfToken = Cookies.get(window.CSRF_COOKIE_NAME);
  if (csrfToken !== undefined) {
    axiosInstance.defaults.headers.common['X-CSRFToken'] = csrfToken;
  }
}

methods.forEach((method) => {
  Object.defineProperty(http, method, {
    get() {
      return <T>(url: string, payload: any = {}, useConfig = {}) => {
        updateAxiosInstance();
        const config = initConfig(useConfig);

        const fetchURL = getFetchURL(url, method, payload);
        const axiosRequest = methodsWithData.includes(method)
          ? axiosInstance[method as Methods]<ServiceResponseData<T>>(fetchURL, payload, config)
          : axiosInstance[method as Methods]<ServiceResponseData<T>>(fetchURL, config);

        return axiosRequest
          .then(response => handleResponse<T>({
            response,
            config,
          }))
          .catch(error => handleReject(error, config));
      };
    },
  });
});

export default http as Http;
