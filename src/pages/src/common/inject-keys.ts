/**
 * Provide/Inject Keys
 * 使用 Symbol 确保类型安全和唯一性
 */

import type { InjectionKey } from 'vue';

/**
 * 更新租户信息的方法接口
 */
export interface UpdateTenantInfo {
  /** 更新租户名称 */
  updateName: (name: string) => void;
  /** 更新租户 Logo */
  updateLogo: (logo: string) => void;
  /** 同时更新租户名称和 Logo */
  updateTenant: (name: string, logo: string) => void;
}

/**
 * 租户信息更新方法的注入 Key
 */
export const UPDATE_TENANT_INFO_KEY: InjectionKey<UpdateTenantInfo> = Symbol('updateTenantInfo');
