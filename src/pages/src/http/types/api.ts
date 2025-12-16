/**
 * 用户角色类型
 * - super_manager: 超级管理员
 * - tenant_manager: 租户管理员
 * - natural_user: 普通用户
 */
export type RoleType = 'super_manager' | 'tenant_manager' | 'natural_user';

export interface CurrentUser {
  username: string
  display_name: string
  role: RoleType
  tenant_id: string
}
