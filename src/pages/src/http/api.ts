import http from './fetch';
import { ResponseData } from './types';
import { CurrentUser } from './types/api';

/** 获取用户信息 */
export const currentUser = () => http.get<ResponseData<CurrentUser>>('/api/v3/web/basic/current-user/');

// 版本日志列表
export const getVersionLogs = () => http.get('/api/v3/web/version-logs/');
