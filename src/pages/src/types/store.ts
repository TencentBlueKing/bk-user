export interface IUser {
  username: string;
  display_name: string;
  role: string;
  tenant_id: string;
}

export interface CurrentOrg {
  tenantId: string;
  tenantName: string;
  deptId?: number;
  deptName?: string;
  organizationPath?: string;
}
