import http from './fetch';

export const currentUser = () => http.get('/api/v1/web/basic/current-user/');

// 版本日志列表
export const getVersionLogs = () => http.get('/api/v1/web/version-logs/');
