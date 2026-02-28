import type { RoleType } from '@/common/constant';

export interface CurrentUser {
  username: string;
  display_name: string;
  role: RoleType;
  tenant_id: string;
}
