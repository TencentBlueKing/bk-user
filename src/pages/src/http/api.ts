import http from './fetch';
import { ResponseData } from './types';
import { CurrentUser, SupportedLanguage } from './types/api';

/** 获取用户信息 */
export const currentUser = () => http.get<ResponseData<CurrentUser>>('/api/v3/web/basic/current-user/');

// 版本日志列表
export const getVersionLogs = () => http.get('/api/v3/web/version-logs/');

/** 获取支持的语言列表 */
export const getSupportedLanguages = () => http.get<ResponseData<SupportedLanguage[]>>('/api/v3/web/basic/languages/');
