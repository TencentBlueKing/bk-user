import http from './fetch';
import type {
  PatchUserEmailParams,
  PatchUserLogoParams,
  PatchUserPhoneParams,
} from './types/personalCenterFiles';

/**
 *个人中心-关联账户列表
 */
export const getCurrentNaturalUser = () => http.get('/api/v1/web/personal-center/current-natural-user/');

/**
 * 个人中心-关联账户详情
 */
export const getPersonalCenterUsers = (id: string) => http.get(`/api/v1/web/personal-center/tenant-users/${id}/`);

/**
 * 租户用户更新邮箱
 */
export const patchUsersEmail = (params: PatchUserEmailParams) => http.put(`/api/v1/web/personal-center/tenant-users/${params.id}/email/`, params);

/**
 * 租户用户更新手机号
 */
export const patchUsersPhone = (params: PatchUserPhoneParams) => http.put(`/api/v1/web/personal-center/tenant-users/${params.id}/phone/`, params);

/**
 * 租户用户更新头像
 */
export const patchTenantUsersLogo = (params: PatchUserLogoParams) => http.put(`/api/v1/web/personal-center/tenant-users/${params.id}/logo/`, params);

/**
 * 个人中心-用户可见字段列表
 */
export const getPersonalCenterUserVisibleFields = (id: string) => http.get(`/api/v1/web/personal-center/tenant-users/${id}/fields/`);

/**
 * 修改用户自定义字段
 */
export const putPersonalCenterUserExtrasFields = (params: any) => http.put(`/api/v1/web/personal-center/tenant-users/${params.id}/extras/`, params);
