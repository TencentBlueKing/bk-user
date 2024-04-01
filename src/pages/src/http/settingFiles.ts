import http from './fetch';
import type {
  NewCustomFieldsParams,
  PatchBuiltinManagerParams,
  PutCustomFieldsParams,
  PutPasswordParams,
  PutRealManagersParams,
  PutTenantInfoParams,
  PutUserValidityParams,
  RealUsersParams,
} from './types/settingFiles';

/**
 * 用户字段列表
 */
export const getFields = () => http.get('/api/v1/web/tenant-setting/fields/');

/**
 * 新建用户自定义字段
 */
export const newCustomFields = (params: NewCustomFieldsParams) => http.post('/api/v1/web/tenant-setting/custom-fields/', params);

/**
 * 修改用户自定义字段
 */
export const putCustomFields = (params: PutCustomFieldsParams) => http.put(`/api/v1/web/tenant-setting/custom-fields/${params.id}/`, params);

/**
 * 删除用户自定义字段
 */
export const deleteCustomFields = (id: string) => http.delete(`/api/v1/web/tenant-setting/custom-fields/${id}/`);

/**
 * 获取当前租户的账户有效期设置
 */
export const getTenantUserValidityPeriod = () => http.get('/api/v1/web/tenant-setting/settings/tenant-user-validity-period/');

/**
 * 更新当前租户的账户有效期设置
 */
export const putTenantUserValidityPeriod = (params: PutUserValidityParams) => http.put('/api/v1/web/tenant-setting/settings/tenant-user-validity-period/', params);

/**
 * 管理员配置-租户内置管理账号信息
 */
export const getBuiltinManager = () => http.get('/api/v1/web/tenant-info/builtin-manager/');

/**
 * 管理员配置-变更内置管理账号密码相关信息
 */
export const patchBuiltinManager = (params: PatchBuiltinManagerParams) => http.patch('/api/v1/web/tenant-info/builtin-manager/', params);

/**
 * 管理员配置-重置内置管理账号密码
 */
export const putBuiltinManagerPassword = (params: PutPasswordParams) => http.put('/api/v1/web/tenant-info/builtin-manager/password/', params);

/**
 * 管理员配置-租户实名管理员列表
 */
export const getRealManagers = () => http.get('/api/v1/web/tenant-info/real-managers/');

/**
 * 管理员配置-租户实名用户列表
 */
export const getRealUsers = (params: RealUsersParams) => http.get('/api/v1/web/tenant-info/real-users/', params);

/**
 * 管理员配置-批量添加租户实名管理员
 */
export const postRealManagers = (params: PutRealManagersParams) => http.post('/api/v1/web/tenant-info/real-managers/', params);

/**
 * 管理员配置-批量移除租户实名管理员
 */
export const deleteRealManagers = (ids: string) => http.delete(`/api/v1/web/tenant-info/real-managers/?ids=${ids}`);

/**
 * 基础设置-租户详情
 */
export const getTenantInfo = () => http.get('/api/v1/web/tenant-info/');

/**
 * 基础设置-更新租户
 */
export const PutTenantInfo = (params: PutTenantInfoParams) => http.put('/api/v1/web/tenant-info/', params);
