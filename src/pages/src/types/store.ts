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
  deptId?: number;
  deptName?: string;
  dataSourceId?: number;
  organizationPath?: string;
}
