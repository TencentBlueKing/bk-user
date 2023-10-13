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
}
