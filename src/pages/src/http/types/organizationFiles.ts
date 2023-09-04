/**
 * 更新租户参数
 */
export interface UpdateTenantParams {
  name: string,
  logo: string,
  manager_ids: string[],
  feature_flags: {
    user_number_visible: boolean,
  },
}

/**
 * 租户部门下用户列表参数
 */
export interface DepartmentsListParams {
  id: string,
  keyword: string,
  page: number,
  pageSize: number,
  recursive: boolean,
}

/**
 * 租户下用户列表参数
 */
export interface TenantListParams {
  id: string,
  keyword: string,
  page: number,
  pageSize: number,
}
