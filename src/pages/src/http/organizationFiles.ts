import http from './fetch';
import type {
  DepartmentsListParams,
  TenantListParams,
  UpdateTenantParams,
} from './types/organizationFiles';

/**
 * 组织架构-租户列表
 */
export const getTenantOrganizationList = () => http.get('/api/v1/web/tenant-organization/tenants/');

/**
 * 单个租户详情
 */
export const getTenantOrganizationDetails = (id: string) => http.get(`/api/v1/web/tenant-organization/tenants/${id}/`);

/**
 * 更新租户
 */
export const putTenantOrganizationDetails = (id: string, params: UpdateTenantParams) => {
  const url = http.put(`/api/v1/web/tenant-organization/tenants/${id}/`, params);
  return url;
};

/**
 * 租户下的二级子部门列表
 */
export const getTenantDepartments = (id: string) => http.get(`/api/v1/web/tenant-organization/departments/${id}/children/`);

/**
 * 租户下部门单个用户详情
 */
export const getTenantUsers = (id: string) => http.get(`/api/v1/web/tenant-organization/users/${id}/`);

/**
 * 租户下部门下用户列表
 */
export const getTenantDepartmentsList = (params: DepartmentsListParams) => {
  const { id, keyword, page, pageSize, recursive  } = params;
  return http.get(`/api/v1/web/tenant-organization/departments/${id}/users/?keyword=${keyword}&page=${page}&page_size=${pageSize}&recursive=${recursive}`);
};

/**
 * 租户下用户列表
 */
export const getTenantUsersList = (params: TenantListParams) => {
  const { id, keyword, page, pageSize } = params;
  return http.get(`/api/v1/web/tenant-organization/tenants/${id}/users/?keyword=${keyword}&page=${page}&page_size=${pageSize}`);
};
