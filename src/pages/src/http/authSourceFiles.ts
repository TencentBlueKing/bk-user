import http from './fetch';
import { ResponseData } from './types';
import type {
  IdpCreateOutput,
  IdpDetail,
  IdpPluginConfigMeta,
  IdpsDataItem,
  IdpsPluginsDataItem,
  NewIdpsParams,
  PatchIdpsParams,
  PutIdpsParams,
} from './types/authSourceFiles';

/**
 * 认证源列表
 */
export const getIdps = (keyword: string) => http.get<ResponseData<IdpsDataItem[]>>(`/api/v3/web/idps/?keyword=${keyword}`);

/**
 * 认证源插件列表
 */
export const getIdpsPlugins = () => http.get<ResponseData<IdpsPluginsDataItem[]>>('/api/v3/web/idps/plugins/');

/**
 * 新建认证源（201，返回认证源 ID 与回调地址）
 */
export const postIdps = (params: NewIdpsParams) => http.post<ResponseData<IdpCreateOutput>>('/api/v3/web/idps/', params);

/**
 * 认证源详情（GET /idps/{id}/，所有插件统一返回 IdpRetrieveOutputSLZ 结构）
 */
export const getIdpsDetails = (id: string) => http.get<ResponseData<IdpDetail>>(`/api/v3/web/idps/${id}/`);

/**
 * 更新认证源部分字段(local)（204 无响应体）
 */
export const patchIdps = (params: PatchIdpsParams) => http.patch<void>(`/api/v3/web/idps/${params.id}/`, params);

/**
 * 更新认证源（204 无响应体）
 */
export const putIdps = (params: PutIdpsParams) => http.put<void>(`/api/v3/web/idps/${params.id}/`, params);

/**
 * 认证源插件配置元信息（JSON Schema）
 */
export const getIdpsPluginsConfig = (id: string) => http.get<ResponseData<IdpPluginConfigMeta>>(`/api/v3/web/idps/plugins/${id}/config-meta/`);
