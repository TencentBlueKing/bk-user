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

/** 移至目标组织参数 */
export interface BatchUpdateParams {
  user_ids: string[];
  target_department_ids: string[];
}

export interface CurrentTenantData {
  id: string;
  name: string;
  logo: string;
  data_sources: {
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
  tenant_id: string;
}
