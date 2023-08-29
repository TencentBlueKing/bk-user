import http from './fetch';
import type {
  NewTenantParams,
  TenantDetailsResult,
  TenantsListResult,
  TenantUpdateParams,
  TenantUsersListParams,
  TenantUsersListResult,
} from './types/tenantsFiles';

/**
 * 获取租户列表
 */
export const getTenants = (): Promise<TenantsListResult> => http.get('/api/v1/web/tenants/');

/**
 * 搜索租户列表
 */
export const searchTenants = (name: string): Promise<TenantsListResult> => http.get(`/api/v1/web/tenants/?name=${name}`);

/**
 * 新建租户
 */
export const createTenants = (params: NewTenantParams) => http.post('/api/v1/web/tenants/', params);

/**
 * 租户详情查询
 */
export const getTenantDetails = (id: string): Promise<TenantDetailsResult> => http.get(`/api/v1/web/tenants/${id}/`);

/**
 * 更新租户
 */
export const putTenants = (id: string, params: TenantUpdateParams) => http.put(`/api/v1/web/tenants/${id}/`, params);

/**
 * 获取租户管理员
 */
export const getTenantUsers = (id: string) => http.get(`/api/v1/web/tenants/${id}/users/`);

/**
 * 获取租户下的用户列表
 */
export const getTenantUsersList = (params: TenantUsersListParams): Promise<TenantUsersListResult> => {
  const { tenantId, keyword, page, pageSize  } = params;
  return http.get(`/api/v1/web/tenants/${tenantId}/users/?keyword=${keyword}&page=${page}&page_size=${pageSize}`);
};
