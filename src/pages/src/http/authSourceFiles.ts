import http from './fetch';
import type {
  NewIdpsParams,
  PatchIdpsParams,
  PutIdpsParams,
} from './types/authSourceFiles';

/**
 * 认证源列表
 */
export const getIdps = (keyword: string) => http.get(`/api/v1/web/idps/?keyword=${keyword}`);

/**
 * 认证源插件列表
 */
export const getIdpsPlugins = () => http.get('/api/v1/web/idps/plugins/');

/**
 * 新建认证源
 */
export const postIdps = (params: NewIdpsParams) => http.post('/api/v1/web/idps/', params);

/**
 * 认证源详情
 */
export const getIdpsDetails = (id: string) => http.get(`/api/v1/web/idps/${id}/`);

/**
 * 更新认证源部分字段(local)
 */
export const patchIdps = (params: PatchIdpsParams) => http.patch(`/api/v1/web/idps/${params.id}/`, params);

/**
 * 更新认证源
 */
export const putIdps = (params: PutIdpsParams) => http.put(`/api/v1/web/idps/${params.id}/`, params);
