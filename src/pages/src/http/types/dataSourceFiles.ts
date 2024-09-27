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
  field_mapping?: [],
  sync_config?: {},
}

/**
 * 更新数据源参数
 */
export interface PutDataSourceParams {
  id: string,
  plugin_config: {},
  field_mapping: [],
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
