/**
 * 新建认证源参数
 */
export interface NewIdpsParams {
  name: string;
  status: string;
  plugin_id: string;
  /** 插件级配置，结构由各插件 schema 决定（local 提交空对象，wecom 为 corp_id/agent_id/secret） */
  plugin_config: Record<string, unknown>;
  data_source_match_rules: DataSourceMatchRule[];
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
  /** 插件级配置，结构由各插件 schema 决定（local 提交空对象，wecom 为 corp_id/agent_id/secret） */
  plugin_config: Record<string, unknown>;
  data_source_match_rules: DataSourceMatchRule[];
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
 * 认证源详情（GET /idps/{id}/ 返回，通用认证源，所有插件统一 IdpRetrieveOutputSLZ 结构）
 */
export interface IdpDetail {
  id: string;
  name: string;
  status: string;
  plugin: IdpsPluginsDataItem;
  plugin_config: Record<string, unknown>;
  callback_uri: string;
  data_source_match_rules: DataSourceMatchRule[];
}

/**
 * 新建认证源返回（IdpCreateOutputSLZ）
 */
export interface IdpCreateOutput {
  id: string;
  callback_uri: string;
}

/**
 * 认证源插件配置元信息返回（IdpPluginConfigMetaRetrieveOutputSLZ）
 */
export interface IdpPluginConfigMeta {
  id: string;
  json_schema: Record<string, unknown>;
}

export interface IdpsPluginsDataItem {
  id: string;
  name: string;
  description: string;
  logo: string;
}

/**
 * 认证源列表项（GET /idps/ 返回，对应 IdpListOutputSLZ）
 */
export interface IdpsDataItem {
  id: string;
  plugin: IdpsPluginsDataItem;
  status: string;
}
