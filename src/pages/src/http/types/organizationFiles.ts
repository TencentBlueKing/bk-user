/**
 * 更新租户参数
 */
export interface UpdateTenantParams {
  name: string;
  logo: string;
  manager_ids: string[];
  feature_flags: {
    user_number_visible: boolean;
  };
}

/**
 * 租户部门下用户列表参数
 */
export interface DepartmentsListParams {
  id: string;
  keyword: string;
  page: number;
  pageSize: number;
  recursive: boolean;
}

/**
 * 租户下用户列表参数
 */
export interface TenantListParams {
  id: string;
  keyword: string;
  page: number;
  pageSize: number;
}

export interface OptionalDepartmentsListData {
  id: number;
  name: string;
  organization_path: string;
}

/**
 * 当前租户下的部门列表参数
 */
export interface GetDepartmentsListParams {
  parent_department_id: number;
  data_source_id?: number;
}

/**
 * 创建部门参数
 */
export interface AddDepartmentParams {
  /** 数据源ID */
  data_source_id: number;
  /** 父部门 ID（为 0 表示创建根部门） */
  parent_department_id?: number;
  /** 部门名称 */
  name: string;
}

/** 创建部门返回 */
export interface AddDepartmentResult {
  id: number;
}

export interface PatchBatchUpdateParams {
  data_source_id: number;
  user_ids: string[];
  target_department_ids: string[];
  source_department_id: string[];
}

/** 移至目标组织参数 */
export interface PutBatchUpdateParams {
  data_source_id: number;
  user_ids: string[];
  target_department_ids: string[];
}

export interface CurrentTenantData {
  id: string;
  name: string;
  logo: string;
  data_sources: {
    name: string;
    id: number;
    type: string;
    plugin_id: string;
    enable_password: boolean;
  }[];
}

export interface DepartmentsItemData {
  id: number;
  name: string;
  has_children: boolean;
  data_source_id: number;
}

export interface SearchKeywordParams {
  keyword: string;
}

export interface SearchOrganizationItemData {
  id: number;
  name: string;
  data_source_id: number;
  organization_path: string;
  tenant_id: string;
  tenant_name: string;
}

export interface SearchUserItemData {
  data_source_id?: number;
  full_name: string;
  id: string;
  organization_paths: string[];
  status: string;
  tenant_id: string;
  tenant_name: string;
  username: string;
}

export interface CollaborationItemData {
  id: string;
  name: string;
  logo: string;
}

export interface TenantsUserItemData {
  data_source_id: number;
  id: string;
  username: string;
  full_name: string;
  status: string;
  email: string;
  phone: string;
  phone_country_code: string;
  departments: string[];
}

export interface TenantsUserListData {
  count: number;
  results: TenantsUserItemData[];
}

export interface GetUserListParams {
  keyword?: string;
  tenant_id?: string;
  data_source_id?: number;
}

export interface OptionalDepartmentsListParams {
  keyword?: string;
  data_source_id: number;
}

/** 租户用户详情 */
export interface TenantsUserDetailData {
  id: string;
  status: string;
  username: string;
  full_name: string;
  email: string;
  phone: string;
  phone_country_code: string;
  account_expired_at: string;
  password_expired_at: string;
  extras: Record<string, string>;
  logo: string;
  language: string;
  time_zone: string;
  departments: {
    id: number;
    name: string;
    organization_path: string;
  }[];
  leaders: {
    id: string;
    username: string;
    full_name: string;
  }[];
}

/** 用户组织路径 */
export interface OrganizationPathsData {
  organization_paths: string[];
}

/** 密码规则 */
export interface PasswordRuleData {
  min_length: number;
  max_length: number;
  contain_lowercase: boolean;
  contain_uppercase: boolean;
  contain_digit: boolean;
  contain_punctuation: boolean;
  not_continuous_count: number;
  not_keyboard_order: boolean;
  not_continuous_letter: boolean;
  not_continuous_digit: boolean;
  not_repeated_symbol: boolean;
  rule_tips: string[];
}

export interface BatchCreatePreviewParams {
  data_source_id: number;
  user_infos: string[];
  department_id: number;
}

export interface OptionalLeaderListParams {
  keyword?: string;
  data_source_id: number;
  exclude_user_id: string;
}

export interface BatchResetPasswordParams {
  data_source_id: number;
  user_ids: string[];
  password: string;
}

export interface BatchLeaderParams {
  data_source_id: number;
  user_ids: string[];
  leader_ids: string[];
}

export interface BatchDeleteUserParams {
  data_source_id: number;
  user_ids: string;
}

export interface BatchCreateParams {
  data_source_id: number;
  user_ids: string[];
  target_department_ids: number[];
}

export interface BatchDeleteParams {
  data_source_id: number;
  user_ids: string;
  source_department_id: number;
}

export interface OptionalLeaderListItemData {
  id: string;
  username: string;
  full_name: string;
}

export interface BatchCreatePreviewItemData {
  username: string;
  full_name: string;
  email: string;
  phone: string;
  phone_country_code: string;
  extras: Record<string, string>;
}
