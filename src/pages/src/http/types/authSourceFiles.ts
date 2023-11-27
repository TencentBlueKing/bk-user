/**
 * 新建认证源参数
 */
export interface NewIdpsParams {
  name: string,
  plugin_id: string,
  plugin_config: {},
  data_source_match_rules?: {
    data_source_id: number,
    field_compare_rules: {
      source_field: string,
      target_field: string,
    }[],
  }[],
}

/**
 * 更新本地认证源部分字段参数
 */
export interface PatchIdpsParams {
  id: string,
  name: string,
}

/**
 * 更新认证源字段参数
 */
export interface PutIdpsParams {
  id: string,
  name: string,
  plugin_config: {},
  data_source_match_rules?: {
    data_source_id: number,
    field_compare_rules: {
      source_field: string,
      target_field: string,
    }[],
  }[],
}
