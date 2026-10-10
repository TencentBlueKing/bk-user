import http, { Config } from './fetch';
import { ResponseData } from './types';
import type {
  AddDepartmentParams,
  AddDepartmentResult,
  BatchCreateParams,
  BatchCreatePreviewItemData,
  BatchCreatePreviewParams,
  BatchDeleteParams,
  BatchDeleteUserParams,
  BatchLeaderParams,
  BatchResetPasswordParams,
  CollaborationItemData,
  CurrentTenantData,
  DepartmentsItemData,
  DepartmentsListParams,
  GetDepartmentsListParams,
  GetOptionalUsersParams,
  GetUserListParams,
  OptionalDepartmentsListData,
  OptionalDepartmentsListParams,
  OptionalLeaderListItemData,
  OptionalLeaderListParams,
  OptionalUserItemData,
  OrganizationPathsData,
  PasswordRuleData,
  PatchBatchUpdateParams,
  PutBatchUpdateParams,
  SearchKeywordParams,
  SearchOrganizationItemData,
  SearchTenantUsersParams,
  SearchUserItemData,
  TenantListParams,
  TenantsUserDetailData,
  TenantsUserListData,
  TenantsUserListParams,
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
export const getCurrentTenant = () => http.get<ResponseData<CurrentTenantData>>(`${prefix}/current-tenant/`);

/**
 * 获取数据源下的部门列表，parent_department_id 为 0 时 / 不传 parent_department_id 均表示获取根部门
 * @param dataSourceId 数据源 ID
 * @param params 查询参数
 */
export const getDepartmentsList = (dataSourceId: number, params: GetDepartmentsListParams) => http.get<ResponseData<DepartmentsItemData[]>>(`${prefix}/tenants/data-sources/${dataSourceId}/departments/`, undefined, { params });

/**
 * 创建租户组织
 */
export const addDepartment = (dataSourceId: number, params: AddDepartmentParams) => http.post<ResponseData<AddDepartmentResult>>(`${prefix}/tenants/data-sources/${dataSourceId}/departments/`, params);

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
export const getCollaboration = () => http.get<ResponseData<CollaborationItemData[]>>(`${prefix}/collaboration-tenants/`);

/**
 * 拉取租户用户列表
 */
export const getTenantsUserList = (tenantId: string, params: TenantsUserListParams, config?: Config) => http.get<ResponseData<TenantsUserListData>>(`${prefix}/tenants/${tenantId}/users/`, params, config);

/**
 * 获取租户用户详情
 */
export const getTenantsUserDetail = (id: string) => http.get<ResponseData<TenantsUserDetailData>>(`${prefix}/tenants/users/${id}/`);

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
export const getOrganizationPaths = (id: string, params?: any) => http.get<ResponseData<OrganizationPathsData>>(`${prefix}/tenants/users/${id}/organization-paths/`, params);

/**
 * 删除租户用户
 */
export const delTenantsUser = (id: string) => http.delete(`${prefix}/tenants/users/${id}/`);

/**
 * 变更租户用户状态（启用/停用）
 */
export const updateTenantsUserStatus = (id: string, params?: any) => http.put(`${prefix}/tenants/users/${id}/status/`, params);


/**
 * 重置租户用户密码
 */
export const resetTenantsUserPassword = (id: string, params: any) => http.put(`${prefix}/tenants/users/${id}/password/`, params);

/** 批量操作 */

/**
 * 批量删除用户
 */
export const batchDeleteUser = (dataSourceId: number, params: BatchDeleteUserParams) => http.delete(`${prefix}/tenants/data-sources/${dataSourceId}/users/operations/batch_delete/`, params);

/**
 * 移出当前组织
 */
export const batchDelete = (dataSourceId: number, params: BatchDeleteParams) => http.delete(`${prefix}/tenants/data-sources/${dataSourceId}/department-user-relations/operations/batch_delete/`, params);

/**
 * 移至目标组织
 */
export const patchBatchUpdate = (dataSourceId: number, params: PatchBatchUpdateParams) => http.patch(`${prefix}/tenants/data-sources/${dataSourceId}/department-user-relations/operations/batch_update/`, params);

/**
 * 从其他组织拉取 / 追加目标组织
 */
export const batchCreate = (dataSourceId: number, params: BatchCreateParams) => http.post(`${prefix}/tenants/data-sources/${dataSourceId}/department-user-relations/operations/batch_create/`, params);

/**
 * 清空并加入组织
 */
export const putBatchUpdate = (dataSourceId: number, params: PutBatchUpdateParams) => http.put(`${prefix}/tenants/data-sources/${dataSourceId}/department-user-relations/operations/batch_update/`, params);

/**
 * 批量停用/启用
 */
export const batchUpdateStatus = (params: any) => http.put(`${prefix}/tenants/users/status/operations/batch_update/`, params);

/**
 * 批量重置密码
 */
export const batchResetPassword = (dataSourceId: number, params: BatchResetPasswordParams) => http.put(`${prefix}/tenants/data-sources/${dataSourceId}/users/password/operations/batch_reset/`, params);

/**
 * 批量续期
 */
export const batchAccountExpired = (params: any) => http.put(`${prefix}/tenants/users/account-expired-at/operations/batch_update/`, params);

/**
 * 批量修改上级
 */
export const batchLeader = (dataSourceId: number, params: BatchLeaderParams) => http.put(`${prefix}/tenants/data-sources/${dataSourceId}/users/leader/operations/batch_update/`, params);

/**
 * 批量修改自定义字段
 */
export const batchCustomField = (dataSourceId: number, params: any) => http.put(`${prefix}/tenants/data-sources/${dataSourceId}/users/custom-field/operations/batch_update/`, params);


/**
 * 快速录入
 */
export const operationsCreate = (dataSourceId: number, params: BatchCreatePreviewParams) => http.post(`${prefix}/tenants/data-sources/${dataSourceId}/users/operations/batch_create/`, params);

/**
 * 快速录入字段 tips 来源
 */
export const getFieldsTips = () => http.get(`${prefix}/tenants/required-user-fields/`);

/**
 * 快速录入数据预览
 */
export const batchCreatePreview = (dataSourceId: number, params: BatchCreatePreviewParams) => http.post<ResponseData<BatchCreatePreviewItemData[]>>(`${prefix}/tenants/data-sources/${dataSourceId}/users/operations/batch_create_preview/`, params);

/**
 * 可选部门
 */
export const optionalDepartmentsList = (dataSourceId: number, params: OptionalDepartmentsListParams) => http.get<ResponseData<OptionalDepartmentsListData[]>>(`${prefix}/tenants/data-sources/${dataSourceId}/optional-departments/`, params);

/**
 * 获取部门可选用户列表（已排除部门内已有用户，用于拉取已有用户）
 */
export const getOptionalUsers = (departmentId: number, params: GetOptionalUsersParams, config?: Config) => http.get<ResponseData<OptionalUserItemData[]>>(`${prefix}/tenants/departments/${departmentId}/optional-users/`, params, config);

/**
 * 可选leader
 */
export const optionalLeaderList = (dataSourceId: number, params: OptionalLeaderListParams, config?: Config) => http.get<ResponseData<OptionalLeaderListItemData[]>>(`${prefix}/tenants/data-sources/${dataSourceId}/optional-leaders/`, params, config);

/**
 * 搜索组织
 */
export const searchOrganization = (params: SearchKeywordParams, config?: Config) => http.get<ResponseData<SearchOrganizationItemData[]>>(`${prefix}/tenants/departments/`, params, config);

/**
 * 获取数据源内用户列表
 */
export const getUsersList = (dataSourceId: number, params: GetUserListParams, config?: Config) => http.get<ResponseData<TenantsUserListData>>(`${prefix}/tenants/data-sources/${dataSourceId}/users/`, params, config);

/**
 * 搜索租户用户（跨数据源，用于全局搜索）
 */
export const searchTenantUsers = (params: SearchTenantUsersParams, config?: Config) => http.get<ResponseData<SearchUserItemData[]>>(`${prefix}/tenants/users/`, params, config);

/**
 * 租户下部门单个用户详情
 */
export const getOrganizationUsers = (id: string) => http.get(`${prefix}/tenants/users/${id}/`);

/**
 * 密码规则
 */
export const passwordRule = (id: string) => http.get<ResponseData<PasswordRuleData>>(`${prefix}/tenants/users/${id}/password-rule/`);

/**
 * 组织树拖拽功能
 */
export const dragOrg = (id: string, params: any) => http.put(`${prefix}/tenants/departments/${id}/parent/`, params);
