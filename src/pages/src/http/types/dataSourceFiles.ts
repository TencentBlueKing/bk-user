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
