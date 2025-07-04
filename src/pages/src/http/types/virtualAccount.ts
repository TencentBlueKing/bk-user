/**
 * 虚拟用户列表参数
 */
export interface VirtualUsersParams {
  page?: number,
  pageSize?: number,
  keyword?: string,
}

/**
 * 新建虚拟用户参数
 */
export interface NewVirtualUsersParams {
  username: string,
  full_name: string,
  app_codes: string[],
  owners: string[],
}

/**
 * 更新虚拟用户参数
 */
export interface PutVirtualUsersParams {
  full_name: string,
  app_codes: string[],
  owners: string[],
}
