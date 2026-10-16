/**
 * 新建认证源参数
 */
export interface NewIdpsParams {
  name: string;
  status: string;
  plugin_id: string;
  plugin_config: {};
  data_source_match_rules?: DataSourceMatchRule[];
}

/**
 * 更新本地认证源部分字段参数
 */
export interface PatchIdpsParams {
  id: string;
  name: string;
}

/**
 * 更新认证源字段参数
 */
export interface PutIdpsParams {
  id: string;
  name: string;
  status: string;
  plugin_config: {};
  data_source_match_rules?: DataSourceMatchRule[];
}

/**
 * 本地认证源插件配置
 * 密码规则/初始密码/登录限制/密码有效期已迁移至本地数据源（plugin_config），此处仅保留账密登录启用开关
 */
export interface LocalIdpPluginConfig {
  enable_password: boolean;
}

/**
 * 数据源匹配规则
 */
export interface DataSourceMatchRule {
  data_source_id: number;
  field_compare_rules: {
    source_field: string;
    target_field: string;
  }[];
}

/**
 * 新建本地认证源参数
 */
export interface NewLocalIdpsParams {
  id?: string;
  name: string;
  status: string;
  plugin_config: LocalIdpPluginConfig;
  data_source_ids: number[];
};

/**
 * 本地认证源详情（getLocalIdps 返回）
 */
export interface LocalIdpDetail {
  id: string;
  name: string;
  status: string;
  plugin_config: LocalIdpPluginConfig;
  data_source_ids: number[];
}

export interface IdpsPluginsDataItem {
  id: string;
  name: string;
  description: string;
  logo: string;
}

export interface IdpsDataItem {
  id: string;
  plugin: IdpsPluginsDataItem;
  status: string;
}
