import http from './fetch';
import type {
  PatchUserEmailParams,
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
export const patchUsersEmail = (params: PatchUserEmailParams) => http.patch(`/api/v1/web/personal-center/tenant-users/${params.id}/email/`, params);

/**
 * 租户用户更新手机号
 */
export const patchUsersPhone = (params: PatchUserPhoneParams) => http.patch(`/api/v1/web/personal-center/tenant-users/${params.id}/phone/`, params);
