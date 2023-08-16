import http from './fetch';

export const currentUser = () => http.get('/api/v1/web/basic/current-user/');
