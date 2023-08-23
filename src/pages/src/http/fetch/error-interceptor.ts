import { Message } from 'bkui-vue';

import type { IFetchConfig } from './index';

import { showLoginModal } from '@/common/auth';

// 请求执行失败拦截器
export default (error: any, config: IFetchConfig) => {
  const {
    code,
    message,
    response,
  } = error;
  switch (code) {
    // 用户登录状态失效
    case 401:
      showLoginModal(response);
  }
  // 全局捕获错误给出提示
  if (config.globalError) {
    Message({ theme: 'error', message });
  }
  return Promise.reject(error);
};
