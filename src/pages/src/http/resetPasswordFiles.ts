import http from './fetch';

/**
 * 发送短信验证码
 */
export const verificationCodes = (params: any) => http.post('/api/v3/web/passwords/operations/reset/methods/phone/verification-codes/', params);

/**
 * 发送重置密码链接到用户邮箱
 */
export const tokenUrls = (params: any) => http.post('/api/v3/web/passwords/operations/reset/methods/email/token-urls/', params);

/**
 * 通过短信验证码获取重置密码链接
 */
export const resetPasswordUrl = (params: any) => http.post('/api/v3/web/passwords/operations/reset/methods/verification-code/token-urls/', params);

/**
 * 根据 Token 获取可重置密码的租户用户列表
 */
export const getUsers = (params: any) => http.get('/api/v3/web/passwords/operations/reset/methods/token/users/', params);

/**
 * 根据 Token 重置密码
 */
export const resetPassword = (params: any) => http.post('/api/v3/web/passwords/operations/reset/methods/token/passwords/', params);
