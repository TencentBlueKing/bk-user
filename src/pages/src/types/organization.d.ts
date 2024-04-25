export interface IOrg {
  id: number;
  name: string;
  has_children: boolean;
  async: boolean;
  children?: IOrg[];
}
