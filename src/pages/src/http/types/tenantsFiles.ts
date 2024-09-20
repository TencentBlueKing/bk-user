/**
 * 获取租户列表返回结果
 */
export interface TenantsListResult {
  id: string,
  name: string,
  status: string,
  logo: string,
  is_default: boolean,
  created_at: string,
}

/**
 * 新建租户信息
 */
export interface NewTenantParams {
  id: string,
  name: string,
  logo?: string,
  status: string,
  fixed_password: string,
  notification_method: string,
  email: string,
  phone: string,
  phone_country_code: string,
}

/**
 * 查询租户详情返回结果
 */
export interface TenantDetailsResult {
  id: string,
  name: string,
  logo: string,
}

/**
 * 更新租户
 */
export interface TenantUpdateParams {
  name: string,
  logo: string,
}

/**
 * 租户下用户列表返回结果
 */
export interface TenantUsersListResult {
  count: number,
  results: {
    id: string,
    username: string,
    full_name: string,
    email: string,
    phone: string,
    phone_country_code: string,
  }[],
}

/**
 * 租户下的用户列表
 */
export interface TenantUsersListParams {
  tenantId: string,
  keyword: string,
  page: number,
  pageSize: number,
}

/**
 * 更新全局配置
 */
export interface GlobalSettingUpdateParams {
  id: string,
  value: boolean,
}

/**
 * 变更内置管理账号密码相关信息
 */
export interface BuiltinManagerParams {
  fixed_password: string,
  notification_method: string,
  email: string,
  phone: string,
  phone_country_code: string,
}
