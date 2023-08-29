/**
 * 获取租户列表返回结果
 */
export interface TenantsListResult {
  id: string,
  name: string,
  logo: string,
  created_at: string,
  managers: {
    id: string,
    username: string,
    full_name: string,
  }[],
  data_sources: {
    id: string,
    name: string,
  }[],
}

/**
 * 新建租户信息
 */
export interface NewTenantParams {
  id: string,
  name: string,
  feature_flags: {
    user_number_visible: boolean,
  },
  logo?: string,
  // password_settings: {
  //   init_password: string,
  //   init_password_method: string,
  //   init_notify_method: string[],
  //   init_mail_config: {},
  //   init_sms_config: {},
  // },
  managers: {
    username: string,
    full_name: string,
    email: string,
    phone: string,
    phone_country_code: string,
  }[],
}

/**
 * 查询租户详情返回结果
 */
export interface TenantDetailsResult {
  id: string,
  name: string,
  logo: string,
  feature_flags: {
    user_number_visible: boolean,
  },
  managers: {
    id: string,
    username: string,
    full_name: string,
    email: string,
    phone: string,
    phone_country_code: string,
  }[],
}

/**
 * 更新租户
 */
export interface TenantUpdateParams {
  name: string,
  logo: string,
  feature_flags: {
    user_number_visible: boolean,
  },
  manager_ids: string[],
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
