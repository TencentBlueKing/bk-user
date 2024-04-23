/**
 * 新建认证源参数
 */
export interface NewIdpsParams {
  name: string,
  status: string,
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
  status: string,
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
 * 新建本地认证源参数
 */
export interface NewLocalIdpsParams {
  id?: string,
  name: string,
  status: string,
  plugin_config: {
    enable_password: boolean,
    password_rule?: object,
    password_initial?: object,
    password_expire?: object,
    login_limit?: object,
  },
};
