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
