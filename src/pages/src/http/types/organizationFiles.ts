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
}

/**
 * 创建部门参数
 */
export interface AddDepartmentParams {
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
  user_ids: string[];
  target_department_ids: string[];
  source_department_id: string[];
}

/** 移至目标组织参数 */
export interface PutBatchUpdateParams {
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

/** 协同租户数据源信息 */
export interface CollaborationDataSourceItem {
  id: number;
  name: string;
  type: string;
  plugin_id: string;
  enable_password: boolean;
}

export interface CollaborationItemData {
  id: string;
  name: string;
  logo: string;
  /** 协同租户下的数据源列表 */
  data_sources: CollaborationDataSourceItem[];
}

/** 租户用户列表查询参数（GET /organization/tenants/{tenant_id}/users/） */
export interface TenantsUserListParams {
  /** 页码 */
  page?: number;
  /** 每页数量 */
  page_size?: number;
  /** 是否递归查询子部门下的用户 */
  recursive?: boolean;
  /** 用户 ID */
  id?: string;
  /** 用户名 */
  username?: string;
  /** 姓名 */
  full_name?: string;
  /** 邮箱 */
  email?: string;
  /** 手机号 */
  phone?: string;
  /** 用户状态（enabled / disabled） */
  status?: string;
  /** 创建时间范围 - 起始 */
  created_at_start?: string;
  /** 创建时间范围 - 结束 */
  created_at_end?: string;
  /** 账号有效期范围 - 起始 */
  account_expired_at_start?: string;
  /** 账号有效期范围 - 结束 */
  account_expired_at_end?: string;
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

/** 数据源内用户列表查询参数（GET /organization/tenants/data-sources/{data_source_id}/users/） */
export interface GetUserListParams extends TenantsUserListParams {
  /** 部门 ID */
  department_id?: number;
}

/** 租户级用户搜索参数（GET /organization/tenants/users/，跨数据源） */
export interface SearchTenantUsersParams {
  keyword?: string;
  tenant_id?: string;
}

export interface OptionalDepartmentsListParams {
  keyword?: string;
}

/** 部门可选用户列表查询参数（GET /organization/tenants/departments/{id}/optional-users/） */
export interface GetOptionalUsersParams {
  /** 搜索关键字（用户名/姓名等聚合模糊匹配） */
  keyword?: string;
}

/** 部门可选用户（已排除部门内已有用户，用于拉取已有用户） */
export interface OptionalUserItemData {
  /** 用户 ID */
  id: string;
  /** 用户名 */
  username: string;
  /** 姓名 */
  full_name: string;
  /** 用户状态（enabled / disabled） */
  status?: string;
  /** 用户所属组织路径 */
  organization_paths: string[];
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
  user_infos: string[];
  department_id: number;
}

export interface OptionalLeaderListParams {
  keyword?: string;
  /** 需要排除的用户 ID（编辑用户时排除自己） */
  excluded_user_id?: string;
}

export interface BatchResetPasswordParams {
  user_ids: string[];
  password: string;
}

export interface BatchLeaderParams {
  user_ids: string[];
  leader_ids: string[];
}

export interface BatchDeleteUserParams {
  user_ids: string;
}

export interface BatchCreateParams {
  user_ids: string[];
  target_department_ids: number[];
}

export interface BatchDeleteParams {
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
