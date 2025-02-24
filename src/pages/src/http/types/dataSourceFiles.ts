/**
 * 数据源用户信息列表返回结果
 */
export interface DataSourceUsersResult {
  id: string,
  username: string,
  full_name: string,
  email: string,
  phone: string,
  departments: {
    id: number,
    name: string,
  }[],
}

/**
 * 新建数据源用户参数
 */
export interface NewDataSourceUserParams {
  id: string,
  username: string,
  full_name: string,
  email: string,
  phone_country_code: string,
  phone: string,
  logo?: string,
  department_ids?: [],
  leader_ids?: [],
}

/**
 * 更新数据源用户参数
 */
export interface PutDataSourceUserParams {
  id: string,
  full_name: string,
  email: string,
  phone_country_code: string,
  phone: string,
  logo?: string,
  department_ids?: [],
  leader_ids?: [],
}

/**
 * 数据源用户信息列表参数
 */
export interface DataSourceUsersParams {
  id: string,
  username: string,
  page: number,
  pageSize: number,
}

/**
 * 新建数据源参数
 */
export interface NewDataSourceParams {
  plugin_id: string,
  plugin_config: {},
  field_mapping?: any[],
  sync_config?: {},
}

/**
 * 更新数据源参数
 */
export interface PutDataSourceParams {
  id: string,
  plugin_config: {},
  field_mapping: any[],
}

/**
 * 部门列表参数
 */
export interface DepartmentsParams {
  id: string,
  name: string,
  page: number,
  pageSize: number,
}

/**
 * 上级列表参数
 */
export interface LeadersParams {
  id: string,
  keyword: string,
  page: number,
  pageSize: number,
}

/**
 * 数据源连通性测试参数
 */
export interface TestConnectionParams {
  plugin_id: string,
  plugin_config: {},
  data_source_id?: string,
}

/**
 * 数据源更新记录参数
 */
export interface SyncRecordsParams {
  page?: number,
  pageSize?: number,
  data_source_id?: number,
  status?: string,
  id: string,
}

/**
 * 生成数据源用户随机密码参数
 */
export interface GeneratePasswordParams {
  data_source_id?: string,
  password_rule_config?: {},
}

/**
 * 数据源用户密码重置参数
 */
export interface ResetPasswordParams {
  id: string,
  password: string,
}

/**
 * 数据源重置参数
 */
export interface DeleteDataSourcesParams {
  id: string,
  is_delete_idp?: string,
}

/**
 * 数据源详情返回值
 */
export interface DataSourceDetails {
  id: number,
  owner_tenant_id: string,
  type: string,
  plugin: {
    id: string,
    name: string,
    description: string,
    logo: string,
  },
  plugin_config: {
    server_config: {
      server_base_url: string,
      server_url: string,
      bind_dn: string,
      bind_password: string,
      base_dn: string,
      user_api_path: string,
      user_api_query_params: any[],
      department_api_path: string,
      department_api_query_params: any[],
      page_size: number,
      request_timeout: number,
      retries: number,
    },
    auth_config: {
      method: string,
      bearer_token: string,
      username: string,
      password: string,
    },
    data_config: {
      user_object_class: string,
      user_search_base_dns: string[],
      dept_object_class: string,
      dept_search_base_dns: string[],
    },
    leader_config: {
      enabled: boolean,
      leader_field: string,
    },
    user_group_config: {
      enabled: boolean,
      object_class: string,
      search_base_dns: string[],
      group_member_field: string,
    },
  },
  sync_config: {
    sync_period: number,
    sync_timeout: number,
  },
  field_mapping: {
    source_field: string,
    mapping_operation: string,
    target_field: string,
  }[],
}

/**
 * 数据源连通性测试返回值
 */
export interface TestConnectionData {
  error_message: string,
  user: {
    code: string,
    properties: {
      username: string,
      full_name: string,
      email: string,
      phone: string,
      phone_country_code: string,
      age: string,
      gender: string,
      region: string,
    },
    leaders: any[],
    departments: string[],
  },
  department: {
    id: string,
    name: string,
    parent: any,
  },
  extras: {
    user_data: {
      departments: string[],
      email: string,
      extras: {
        age: string,
        gender: string,
        region: string,
      },
      full_name: string,
      id: string,
      leaders: any[],
      phone: string,
      phone_country_code: string,
      username: string,
    },
    department_data: {
      id: string,
      name: string,
      parent: any,
    },
  },
}

export interface SyncRecords {
  count: number,
  results: {
    id: number,
    status: string,
    has_warning: boolean,
    trigger: string,
    operator: string,
    start_at: string,
    duration: string,
    extras: {
      incremental: boolean,
      overwrite: boolean,
      async_run: boolean,
      sync_timeout: number,
    }
  }[],
}
