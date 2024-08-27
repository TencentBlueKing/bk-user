import http from './fetch';
import type {
  DepartmentsListParams,
  TenantListParams,
  UpdateTenantParams,
} from './types/organizationFiles';

const prefix = 'api/v3/web/organization';

/**
 * 组织架构-租户列表
 */
export const getTenantOrganizationList = () => http.get('/api/v3/web/tenant-organization/tenants/');

/**
 * 单个租户详情
 */
export const getTenantOrganizationDetails = (id: string) => http.get(`/api/v3/web/tenant-organization/tenants/${id}/`);

/**
 * 更新租户
 */
export const putTenantOrganizationDetails = (id: string, params: UpdateTenantParams) => {
  const url = http.put(`/api/v3/web/tenant-organization/tenants/${id}/`, params);
  return url;
};

/**
 * 租户下的二级子部门列表
 */
export const getTenantDepartments = (id: string) => http.get(`/api/v3/web/tenant-organization/departments/${id}/children/`);


/**
 * 租户下部门下用户列表
 */
export const getTenantDepartmentsList = (params: DepartmentsListParams) => {
  const { id, keyword, page, pageSize, recursive  } = params;
  return http.get(`/api/v3/web/tenant-organization/departments/${id}/users/?keyword=${keyword}&page=${page}&page_size=${pageSize}&recursive=${recursive}`);
};

/**
 * 租户下用户列表
 */
export const getTenantOrganizationUsersList = (params: TenantListParams) => {
  const { id, keyword, page, pageSize } = params;
  return http.get(`/api/v3/web/tenant-organization/tenants/${id}/users/?keyword=${keyword}&page=${page}&page_size=${pageSize}`);
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
export const getCollaboration = () => http.get(`${prefix}/collaboration-tenants/`);

/**
 * 拉取租户用户列表
 */
export const getTenantsUserList = (id: string, params: any) => http.get(`${prefix}/tenants/${id}/users/`, params);

/**
 * 获取租户用户详情
 */
export const getTenantsUserDetail = (id: string) => http.get(`${prefix}/tenants/users/${id}/`);

/**
 * 租户用户续期
 */
export const updateAccountExpiredAt = (id: string, params: any) => http.put(`${prefix}/tenants/users/${id}/account-expired-at/`, params);

/**
 * 更新租户用户
 */
export const updateTenantsUserDetail = (id: string, params: any) => http.put(`${prefix}/tenants/users/${id}/`, params);

/**
 * 更新租户用户
 */
export const getOrganizationPaths = (id: string, params: any) => http.get(`${prefix}/tenants/users/${id}/organization-paths/`, params);

/**
 * 删除租户用户
 */
export const delTenantsUser = (id: string) => http.delete(`${prefix}/tenants/users/${id}/`);

/**
 * 变更租户用户状态（启用/停用）
 */
export const updateTenantsUserStatus = (id: string, params: any) => http.put(`${prefix}/tenants/users/${id}/status/`, params);


/**
 * 重置租户用户密码
 */
export const resetTenantsUserPassword = (id: string, params: any) => http.put(`${prefix}/tenants/users/${id}/password/`, params);

/** 批量操作 */

/**
 * 批量删除用户
 */
export const batchDeleteUser = (user_ids: any) => http.delete(`${prefix}/tenants/users/operations/batch_delete/`, { user_ids });

/**
 * 移出当前组织
 */
export const batchDelete = (params: any) => http.delete(`${prefix}/tenants/department-user-relations/operations/batch_delete/`, params);

/**
 * 移至目标组织
 */
export const batchUpdate = (params: any) => http.patch(`${prefix}/tenants/department-user-relations/operations/batch_update/`, params);

/**
 * 从其他组织拉取 / 追加目标组织
 */
export const batchCreate = (params: any) => http.post(`${prefix}/tenants/department-user-relations/operations/batch_create/`, params);

/**
 * 清空并加入组织
 */
export const batchDelUpdate = (params: any) => http.put(`${prefix}/tenants/department-user-relations/operations/batch_update/`, params);

/**
 * 批量停用/启用
 */
export const batchUpdateStatus = (params: any) => http.put(`${prefix}/tenants/users/status/operations/batch_update/`, params);

/**
 * 批量重置密码
 */
export const batchResetPassword = (params: any) => http.put(`${prefix}/tenants/users/password/operations/batch_reset/`, params);

/**
 * 批量续期
 */
export const batchAccountExpired = (params: any) => http.put(`${prefix}/tenants/users/account-expired-at/operations/batch_update/`, params);

/**
 * 批量修改上级
 */
export const batchLeader = (params: any) => http.put(`${prefix}/tenants/users/leader/operations/batch_update/`, params);

/**
 * 批量修改自定义字段
 */
export const batchCustomField = (params: any) => http.put(`${prefix}/tenants/users/custom-field/operations/batch_update/`, params);


/**
 * 快速录入
 */
export const operationsCreate = (params: any) => http.post(`${prefix}/tenants/users/operations/batch_create/`, params);

/**
 * 快速录入字段 tips 来源
 */
export const getFieldsTips = () => http.get(`${prefix}/tenants/required-user-fields/`);

/**
 * 快速录入数据预览
 */
export const batchCreatePreview = (params: any) => http.post(`${prefix}/tenants/users/operations/batch_create_preview/`, params);

/**
 * 可选部门
 */
export const optionalDepartmentsList = (params: any) => http.get(`${prefix}/tenants/optional-departments/`, params);

/**
 * 可选leader
 */
export const optionalLeaderList = (params: any) => http.get(`${prefix}/tenants/optional-leaders/`, params);

/**
 * 搜索组织
 */
export const searchOrganization = (params: any) => http.get(`${prefix}/tenants/departments/`, params);

/**
 * 搜索用户
 */
export const searchUser = (params: any) => http.get(`${prefix}/tenants/users/`, params);

/**
 * 租户下部门单个用户详情
 */
export const getOrganizationUsers = (id: string) => http.get(`${prefix}/tenants/users/${id}/`);

/**
 * 搜索租户用户
 */
export const getUsersList = (params: any) => http.get(`${prefix}/tenants/users/`, params);

/**
 * 密码规则
 */
export const passwordRule = (id: string) => http.get(`${prefix}/tenants/users/${id}/password-rule/`);

/**
 * 组织树拖拽功能
 */
export const dragOrg = (id: string, params: any) => http.put(`${prefix}/tenants/departments/${id}/parent/`, params);
