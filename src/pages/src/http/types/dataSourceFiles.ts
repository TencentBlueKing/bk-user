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
  name: string,
  plugin_id: string,
  plugin_config: {},
  field_mapping: [],
}

/**
 * 更新数据源参数
 */
export interface PutDataSourceParams {
  id: string,
  plugin_config: {},
  field_mapping: [],
}
