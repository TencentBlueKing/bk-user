export interface IUser {
  username: string;
  display_name: string;
  role: string;
  tenant_id: string;
}

export interface SelectedOrg {
  tenantId: string;
  tenantName: string;
  tenantLogo: string;
  deptId?: number;
  deptName?: string;
  organizationPath?: string;
}
