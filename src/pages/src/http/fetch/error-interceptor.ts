import { Message } from 'bkui-vue';

import { showLoginModal } from '@blueking/login-modal';

import type { IFetchConfig } from './index';

import { getLoginUrl } from '@/common/auth';

// 请求执行失败拦截器
export default (error: any, config: IFetchConfig) => {
  const {
    code,
    message,
  } = error;
  switch (code) {
    // 用户登录状态失效
    case 401:
      // 登录弹窗
      showLoginModal({ getLoginUrl });
      break;
  }

  // 全局捕获错误给出提示
  if (config.globalError) {
    Message({ theme: 'error', message });
  }
  return Promise.reject(error);
};
