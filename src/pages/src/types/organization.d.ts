import { DepartmentsItemData } from '@/http/types/organizationFiles';

export interface IOrg extends DepartmentsItemData {
  async?: boolean;
  children?: IOrg[];
}
