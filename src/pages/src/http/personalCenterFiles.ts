import { AxiosRequestConfig } from 'axios';

import http from './fetch';
import type {
  PatchUserEmailParams,
  PatchUserLogoParams,
  PatchUserPhoneParams,
  postPersonalCenterUserEmailCaptchaParams,
  postPersonalCenterUserPhoneCaptchaParams,
  PutUserPasswordParams,
} from './types/personalCenterFiles';
interface Config extends AxiosRequestConfig {
  globalError?: boolean
}
/**
 *个人中心-关联账户列表
 */
export const getCurrentNaturalUser = () => http.get('/api/v3/web/personal-center/current-natural-user/');

/**
 * 个人中心-关联账户详情
 */
export const getPersonalCenterUsers = (id: string) => http.get(`/api/v3/web/personal-center/tenant-users/${id}/`);

/**
 * 租户用户更新邮箱
 */
export const patchUsersEmail = (params: PatchUserEmailParams, config: Config) => http.put(`/api/v3/web/personal-center/tenant-users/${params.id}/email/`, params, config);

/**
 * 租户用户更新手机号
 */
export const patchUsersPhone = (params: PatchUserPhoneParams, config: Config) => http.put(`/api/v3/web/personal-center/tenant-users/${params.id}/phone/`, params, config);

/**
 * 租户用户更新头像
 */
export const patchTenantUsersLogo = (params: PatchUserLogoParams) => http.put(`/api/v3/web/personal-center/tenant-users/${params.id}/logo/`, params);

/**
 * 个人中心-用户可见字段列表
 */
export const getPersonalCenterUserVisibleFields = (id: string) => http.get(`/api/v3/web/personal-center/tenant-users/${id}/fields/`);

/**
 * 修改用户自定义字段
 */
export const putPersonalCenterUserExtrasFields = (params: any) => http.put(`/api/v3/web/personal-center/tenant-users/${params.id}/extras/`, params);

/**
 * 租户用户更新语言
 */
export const putUserLanguage = (params: any) => http.put(`/api/v3/web/personal-center/tenant-users/${params.id}/language/`, params);

/**
 * 租户用户更新时区
 */
export const putUserTimeZone = (params: any) => http.put(`/api/v3/web/personal-center/tenant-users/${params.id}/time-zone/`, params);

/**
 * 个人中心修改密码
 */
export const putPersonalCenterUserPassword = (params: PutUserPasswordParams) => http.put(`/api/v3/web/personal-center/tenant-users/${params.id}/password/`, params);

/**
 * 个人中心-用户功能特性-当前用户是否支持修改密码
 */
export const getPersonalCenterUserFeature = (id: string) => http.get(`/api/v3/web/personal-center/tenant-users/${id}/feature-flags/`);

/**
 * 个人中心-租户修改手机号时，发送验证码
 */
export const postPersonalCenterUserPhoneCaptcha = (id: string, params: postPersonalCenterUserPhoneCaptchaParams) => http.post(`/api/v3/web/personal-center/tenant-users/${id}/phone-verification-code/`, params);

/**
 * 个人中心-租户修改邮箱时，发送验证码
 */
export const postPersonalCenterUserEmailCaptcha = (id: string, params: postPersonalCenterUserEmailCaptchaParams) => http.post(`/api/v3/web/personal-center/tenant-users/${id}/email-verification-code/ `, params);
