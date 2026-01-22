/**
 * 用户角色类型
 * - super_manager: 租户管理员
 * - tenant_manager: 内置管理员
 * - natural_user: 普通用户
 */
export type RoleType = 'super_manager' | 'tenant_manager' | 'natural_user';

/**
 * @description 用户角色类型
 * - super_manager: 租户管理员 - 此处语义虽为超级管理员，但本项目对应的是"租户管理员"
 * - tenant_manager: 内置管理员 - 此处语义虽为超级管理员，但本项目对应的是"内置管理员"
 * - natural_user: 普通用户
 */
export const ROLE: Record<string, RoleType> = {
  /** 租户管理员 */
  SUPER_MANAGER: 'super_manager',
  /** 内置管理员 */
  TENANT_MANAGER: 'tenant_manager',
  /** 普通用户 */
  NATURAL_USER: 'natural_user',
};
