export interface IUser {
  username: string;
  display_name: string;
  role: string;
  tenant_id: string;
  time_zone: string;
  language: string;
}

export interface SelectedOrg {
  tenantId: string;
  tenantName: string;
  tenantLogo: string;
  nodeType?: 'tenant' | 'source' | 'department';
  deptId?: number;
  deptName?: string;
  dataSourceId?: number;
  organizationPath?: string;
}
