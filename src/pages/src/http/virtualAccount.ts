import http from './fetch';
import type {
  NewVirtualUsersParams,
  PutVirtualUsersParams,
  VirtualUsersParams,
} from './types/virtualAccount';

/**
 * 虚拟用户列表
 */
export const getVirtualUsers = (params: VirtualUsersParams) => {
  const { keyword, page, pageSize } = params;
  return http.get(`/api/v1/web/virtual-users/?keyword=${keyword}&page=${page}&page_size=${pageSize}`);
};

/**
 * 新建虚拟用户
 */
export const newVirtualUsers = (params: NewVirtualUsersParams) => http.post('/api/v1/web/virtual-users/', params);

/**
 * 虚拟用户详情
 */
export const getVirtualUsersDetail = (id: string) => http.get(`/api/v1/web/virtual-users/${id}/`);

/**
 * 更新虚拟用户
 */
export const putVirtualUsers = (id: string, params: PutVirtualUsersParams) => http.put(`/api/v1/web/virtual-users/${id}/`, params);

/**
 * 删除虚拟用户
 */
export const deleteVirtualUsers = (id: string) => http.delete(`/api/v1/web/virtual-users/${id}/`);
