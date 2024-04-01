/**
 * 新建用户自定义字段
 */
export interface NewCustomFieldsParams {
  name: string,
  display_name: string,
  data_type: string,
  required: boolean,
  default: {},
  options: {},
}

/**
 * 修改用户自定义字段
 */
export interface PutCustomFieldsParams {
  id: number,
  display_name: string,
  required: boolean,
  default: {},
  options: {},
  data_type: string,
  unique: string,
  personal_center_visible: boolean,
  personal_center_editable: boolean,
  manager_editable: boolean,
  mapping: {},
}

/**
 * 更新当前租户账户有效期设置字段
 */
export interface PutUserValidityParams {
  enabled: boolean
  validity_period: number,
  remind_before_expire: number[],
  enabled_notification_methods: string[],
  notification_templates: [],
}

/**
 * 管理员配置-变更内置管理员账号密码相关信息
 */
export interface PatchBuiltinManagerParams {
  username?: string,
  enable_account_password_login?: boolean,
}

/**
 * 管理员配置-重置内置管理账号密码参数
 */
export interface PutPasswordParams {
  password: string,
}

/**
 * 管理员配置-租户实名用户列表参数
 */
export interface RealUsersParams {
  page?: number,
  page_size?: number,
  keyword?: string,
}

/**
 * 管理员配置-修改租户实名管理员账号列表参数
 */
export interface PutRealManagersParams {
  ids: string[],
}

/**
 * 管理员配置-更新租户
 */
export interface PutTenantInfoParams {
  name: string,
  logo?: string,
  visible: boolean,
  user_number_visible: boolean,
}
