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
 * 本地认证源密码规则
 */
export interface LocalIdpPasswordRule {
  min_length: number;
  contain_lowercase: boolean;
  contain_uppercase: boolean;
  contain_digit: boolean;
  contain_punctuation: boolean;
  not_continuous_count: number;
  not_keyboard_order: boolean;
  not_continuous_letter: boolean;
  not_continuous_digit: boolean;
  not_repeated_symbol: boolean;
}

/**
 * 通知模板
 */
export interface NotificationTemplate {
  method: string;
  scene: string;
  title: string | null;
  sender: string;
  content: string;
  content_html: string;
}

/**
 * 通知配置
 */
export interface NotificationConfig {
  enabled_methods: string[];
  templates: NotificationTemplate[];
}

/**
 * 本地认证源 - 初始密码配置
 */
export interface LocalIdpPasswordInitial {
  cannot_use_previous_password: boolean;
  reserved_previous_password_count: number;
  generate_method: 'random' | 'fixed';
  fixed_password?: string | null;
  notification: NotificationConfig;
}

/**
 * 本地认证源 - 密码有效期配置
 */
export interface LocalIdpPasswordExpire {
  valid_time: number;
  remind_before_expire: number[];
  notification: NotificationConfig;
}

/**
 * 本地认证源 - 登录限制配置
 */
export interface LocalIdpLoginLimit {
  force_change_at_first_login: boolean;
  max_retries: number;
  lock_time: number;
}

/**
 * 本地认证源插件配置
 */
export interface LocalIdpPluginConfig {
  enable_password: boolean;
  password_rule: LocalIdpPasswordRule;
  password_initial: LocalIdpPasswordInitial;
  password_expire: LocalIdpPasswordExpire;
  login_limit: LocalIdpLoginLimit;
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
