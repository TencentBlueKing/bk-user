/**
 * 同步配置
 */
export interface SyncConfig {
  sync_period: number;
  sync_timeout: number;
}

/**
 * 字段映射
 */
export interface FieldMapping {
  source_field: string;
  mapping_operation: string;
  target_field: string;
  expression?: any;
}

/**
 * 数据源用户信息列表返回结果
 */
export interface DataSourceUsersResult {
  id: string;
  username: string;
  full_name: string;
  email: string;
  phone: string;
  departments: {
    id: number;
    name: string;
  }[];
}

/**
 * 新建数据源用户参数
 */
export interface NewDataSourceUserParams {
  id: string;
  username: string;
  full_name: string;
  email: string;
  phone_country_code: string;
  phone: string;
  logo?: string;
  department_ids?: [];
  leader_ids?: [];
}

/**
 * 更新数据源用户参数
 */
export interface PutDataSourceUserParams {
  id: string;
  full_name: string;
  email: string;
  phone_country_code: string;
  phone: string;
  logo?: string;
  department_ids?: [];
  leader_ids?: [];
}

/**
 * 数据源用户信息列表参数
 */
export interface DataSourceUsersParams {
  id: string;
  username: string;
  page: number;
  pageSize: number;
}

/**
 * 新建数据源参数
 */
export interface UsernameGenerateConfig {
  rule: 'unchanged' | 'add_affix';
  prefix: string;
  suffix: string;
}

export interface NewDataSourceParams {
  plugin_id: string;
  name: string;
  plugin_config: GeneralDataSourcePluginConfig | LDAPDataSourcePluginConfig | LocalDataSourcePluginConfig;
  field_mapping?: FieldMapping[];
  sync_config?: SyncConfig;
  username_generate_config?: UsernameGenerateConfig;
}

/**
 * 新建数据源返回值
 */
export interface NewDataSourceResult {
  id: number;
}

/**
 * 更新数据源参数
 */
export interface PutDataSourceParams {
  name: string;
  plugin_config: {};
  field_mapping: FieldMapping[];
  sync_config?: SyncConfig;
}

/**
 * 部门列表参数
 */
export interface DepartmentsParams {
  id: string;
  name: string;
  page: number;
  pageSize: number;
}

/**
 * 上级列表参数
 */
export interface LeadersParams {
  id: string;
  keyword: string;
  page: number;
  pageSize: number;
}

/**
 * 数据源连通性测试参数
 */
export interface TestConnectionParams {
  plugin_id: string;
  plugin_config: {};
  data_source_id?: number;
}

/**
 * 数据源更新记录参数
 */
export interface SyncRecordsParams {
  page?: number;
  page_size?: number;
  data_source_id?: number;
  plugin_id?: string;
  statuses?: string;
}

/**
 * 生成数据源用户随机密码参数
 */
export interface GeneratePasswordParams {
  data_source_id?: number;
  password_rule_config?: {};
}

/** 生成随机密码返回值 */
export interface RandomPasswordsData {
  password: string;
}

/**
 * 数据源用户密码重置参数
 */
export interface ResetPasswordParams {
  id: string;
  password: string;
}

/**
 * 数据源重置参数
 */
export interface DeleteDataSourcesParams {
  id: number;
  is_delete_idp?: string;
}

/**
 * 数据源详情返回值
 */
export interface DataSourceDetails {
  id: number;
  /** 数据源名称 */
  name?: string;
  owner_tenant_id: string;
  type: string;
  plugin: {
    id: string;
    name: string;
    description: string;
    logo: string;
  };
  plugin_config: {
    server_config: ServerConfig;
    auth_config: AuthConfig;
    data_config: DataConfig;
    leader_config: LeaderConfig;
    user_group_config: UserGroupConfig;
  };
  sync_config: SyncConfig;
  field_mapping: FieldMapping[];
  username_generate_config: {
    rule: 'unchanged' | 'add_affix';
    prefix: string;
    suffix: string;
  };
}

/**
 * 数据源连通性测试返回值
 */
export interface TestConnectionData {
  error_message: string;
  user: {
    code: string;
    properties: {
      username: string;
      full_name: string;
      email: string;
      phone: string;
      phone_country_code: string;
      age: string;
      gender: string;
      region: string;
    };
    leaders: any[];
    departments: string[];
  };
  department: {
    id: string;
    name: string;
    parent: any;
  };
  extras: {
    user_data: {
      departments: string[];
      email: string;
      extras: {
        age: string;
        gender: string;
        region: string;
      };
      full_name: string;
      id: string;
      leaders: any[];
      phone: string;
      phone_country_code: string;
      username: string;
    };
    department_data: {
      id: string;
      name: string;
      parent: any;
    };
  };
}

export interface SyncRecords {
  count: number;
  results: {
    id: number;
    data_source_id?: number;
    data_source_name?: string;
    status: string;
    has_warning: boolean;
    trigger: string;
    operator: string;
    start_at: string;
    duration: string;
    extras: {
      incremental: boolean;
      overwrite: boolean;
      async_run: boolean;
      sync_timeout: number;
    }
  }[];
}

export interface GetDataSourceListParams {
  type?: 'real' | 'virtual' | 'builtin_management';
}

export interface DataSourceItemData {
  name: string;
  id: number;
  owner_tenant_id: string;
  type: string;
  plugin_id: string;
}

export interface OperationsSyncData {
  status: string;
  summary: string;
  task_id: string;
}

export interface DataSourcePluginsItemData {
  id: string;
  name: string;
  description: string;
  logo: string;
}

/**
 * 查询参数
 */
export interface QueryParam {
  key: string;
  value: string;
}

/**
 * 服务器配置
 */
export interface ServerConfig {
  server_base_url?: string;
  server_url?: string;
  user_api_path?: string;
  user_api_query_params?: QueryParam[];
  department_api_path?: string;
  department_api_query_params?: QueryParam[];
  bind_dn?: string;
  bind_password?: string;
  base_dn?: string;
  page_size?: number;
  request_timeout?: number;
  retries?: number;
}

/**
 * 认证配置
 */
export interface AuthConfig {
  method?: 'bearer_token' | 'basic_auth' | 'bk_apigateway';
  bearer_token?: string;
  username?: string;
  password?: string;
  gateway_name?: string;
  gateway_stage?: string;
  tenant_id?: string;
}

/**
 * 数据配置
 */
export interface DataConfig {
  user_object_class?: string;
  user_search_base_dns?: string[];
  dept_object_class?: string;
  dept_search_base_dns?: string[];
  uuid_attribute?: string;
}

/**
 * Leader 配置
 */
export interface LeaderConfig {
  enabled?: boolean;
  leader_field?: string;
}

/**
 * 用户组配置
 */
export interface UserGroupConfig {
  enabled?: boolean;
  object_class?: string;
  search_base_dns?: string[];
  group_member_field?: 'member' | 'uniqueMember';
}

/**
 * 通用数据源插件配置
 */
export interface GeneralDataSourcePluginConfig {
  server_config?: ServerConfig;
  auth_config?: AuthConfig;
}

/**
 * LDAP 数据源插件配置
 */
export interface LDAPDataSourcePluginConfig {
  server_config: ServerConfig;
  data_config: DataConfig;
  user_group_config: UserGroupConfig;
  leader_config: LeaderConfig;
}

/**
 * 本地数据源插件配置
 */
export interface LocalDataSourcePluginConfig {
  enable_password?: boolean;
  password_rule?: Record<string, any>;
  password_initial?: Record<string, any>;
  password_expire?: Record<string, any>;
  login_limit?: Record<string, any>;
}

/**
 * 数据源插件默认配置返回值
 */
export interface DataSourcePluginDefaultConfig {
  config: GeneralDataSourcePluginConfig | LDAPDataSourcePluginConfig | LocalDataSourcePluginConfig;
}

/**
 * 数据源关联资源统计信息
 */
export interface RelatedResourceStatistics {
  own_department_count: number;
  own_user_count: number;
  shared_to_tenant_count: number;
  shared_to_department_count: number;
  shared_to_user_count: number;
}

export interface BatchDeleteDataSourcesParams {
  is_delete_idp?: boolean;
}
