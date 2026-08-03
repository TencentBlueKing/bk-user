import { DepartmentsItemData } from '@/http/types/organizationFiles';

export type OrganizationNodeType = 'source' | 'department';

export interface IOrg extends Partial<DepartmentsItemData> {
  nodeType?: OrganizationNodeType;
  treeKey?: string;
  departmentId?: number;
  logo?: string;
  plugin_id?: string;
  async?: boolean;
  children?: IOrg[];
}
