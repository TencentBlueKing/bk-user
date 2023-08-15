import type { IFetchConfig } from './index';
import RequestError from './request-error';

// 请求成功执行拦截器
export default async (response: any, config: IFetchConfig) => {
  const {
    code = response.code,
    data,
    message = response.statusText,
  } = await response[config.responseType]();
  if (response.ok) {
    // 对应 HTTP 请求的状态码 200 到 299
    // 校验接口返回的数据，status 为 0 表示业务成功
    switch (code) {
      // 接口请求成功
      case 0:
        return Promise.resolve(data);
      // 后端业务处理报错
      default:
        throw new RequestError(code, message || '系统错误', data);
    }
  } else {
    // 处理 http 非 200 异常
    throw new RequestError(code || -1, message || '系统错误', data);
  }
};
