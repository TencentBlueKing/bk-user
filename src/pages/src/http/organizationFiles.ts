import http from './fetch';
import type {
  DepartmentsListParams,
  TenantListParams,
  UpdateTenantParams,
} from './types/organizationFiles';

const prefix = 'api/v1/web/organization';

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
export const getTenantOrganizationUsers = (id: string) => http.get(`/api/v1/web/tenant-organization/users/${id}/`);

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
export const getTenantOrganizationUsersList = (params: TenantListParams) => {
  const { id, keyword, page, pageSize } = params;
  return http.get(`/api/v1/web/tenant-organization/tenants/${id}/users/?keyword=${keyword}&page=${page}&page_size=${pageSize}`);
};

/**
 * 当前租户
 */
export const getCurrentTenant = () => http.get(`${prefix}/current-tenant/`);

/**
 * 当前租户下的部门列表，id为0时表示获取根部门
 */
export const getDepartmentsList = (deptId: number, id: string) => http.get(`${prefix}/tenants/${id}/departments/`, { parent_department_id: deptId });

/**
 * 创建租户组织
 */
export const addDepartment = (id: string, params: any) => http.post(`${prefix}/tenants/${id}/departments/`, params);

/**
 * 删除租户组织
 */
export const deleteDepartment = (id: string) => http.delete(`${prefix}/tenants/departments/${id}/`);

/**
 * 更新租户组织
 */
export const updateDepartment = (id: string, params: any) => http.put(`${prefix}/tenants/departments/${id}/`, params);

/**
 * 获取当前租户的协作租户信息
 */
export const getCollaboration = () => http.get(`${prefix}/collaborative-tenants/`);

/**
 * 搜索组织
 */
export const searchOrganization = (params: any) => http.get(`${prefix}/tenants/departments/`, params);

/**
 * 搜索用户
 */
export const searchUser = (params: any) => http.get(`${prefix}/tenants/users/`, params);
