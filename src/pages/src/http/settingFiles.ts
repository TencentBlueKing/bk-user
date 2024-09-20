import http from './fetch';
import type {
  CollaborationSyncRecordsParams,
  FromStrategiesConfirmParams,
  NewCustomFieldsParams,
  NewToStrategiesParams,
  PatchBuiltinManagerParams,
  PutCustomFieldsParams,
  PutPasswordParams,
  PutRealManagersParams,
  PutTenantInfoParams,
  PutUserValidityParams,
  RealUsersParams,
  TenantItem,
} from './types/settingFiles';

/**
 * 用户字段列表
 */
export const getFields = () => http.get('/api/v3/web/tenant-setting/fields/');

/**
 * 新建用户自定义字段
 */
export const newCustomFields = (params: NewCustomFieldsParams) => http.post('/api/v3/web/tenant-setting/custom-fields/', params);

/**
 * 修改用户自定义字段
 */
export const putCustomFields = (params: PutCustomFieldsParams) => http.put(`/api/v3/web/tenant-setting/custom-fields/${params.id}/`, params);

/**
 * 删除用户自定义字段
 */
export const deleteCustomFields = (id: string) => http.delete(`/api/v3/web/tenant-setting/custom-fields/${id}/`);

/**
 * 获取当前租户的账户有效期设置
 */
export const getTenantUserValidityPeriod = () => http.get('/api/v3/web/tenant-setting/settings/tenant-user-validity-period/');

/**
 * 更新当前租户的账户有效期设置
 */
export const putTenantUserValidityPeriod = (params: PutUserValidityParams) => http.put('/api/v3/web/tenant-setting/settings/tenant-user-validity-period/', params);

/**
 * 管理员配置-租户内置管理账号信息
 */
export const getBuiltinManager = () => http.get('/api/v3/web/tenant-info/builtin-manager/');

/**
 * 管理员配置-变更内置管理账号密码相关信息
 */
export const patchBuiltinManager = (params: PatchBuiltinManagerParams) => http.patch('/api/v3/web/tenant-info/builtin-manager/', params);

/**
 * 管理员配置-重置内置管理账号密码
 */
export const putBuiltinManagerPassword = (params: PutPasswordParams) => http.put('/api/v3/web/tenant-info/builtin-manager/password/', params);

/**
 * 管理员配置-租户实名管理员列表
 */
export const getRealManagers = () => http.get('/api/v3/web/tenant-info/real-managers/');

/**
 * 管理员配置-租户实名用户列表
 */
export const getRealUsers = (params: RealUsersParams) => http.get('/api/v3/web/tenant-info/real-users/', params);

/**
 * 管理员配置-批量添加租户实名管理员
 */
export const postRealManagers = (params: PutRealManagersParams) => http.post('/api/v3/web/tenant-info/real-managers/', params);

/**
 * 管理员配置-批量移除租户实名管理员
 */
export const deleteRealManagers = (ids: string) => http.delete(`/api/v3/web/tenant-info/real-managers/?ids=${ids}`);

/**
 * 基础设置-租户详情
 */
export const getTenantInfo = () => http.get('/api/v3/web/tenant-info/');

/**
 * 基础设置-更新租户
 */
export const PutTenantInfo = (params: PutTenantInfoParams) => http.put('/api/v3/web/tenant-info/', params);

/**
 * 跨租户协同-我分享的协同策略
 */
export const getToStrategies = () => http.get('/api/v3/web/collaboration/to-strategies/');

/**
 * 跨租户协同-我分享的协同策略切换状态
 */
export const putToStrategiesStatus = (id: number) => http.put(`/api/v3/web/collaboration/to-strategies/${id}/source-status/`);

/**
 * 跨租户协同-新建协同策略
 */
export const postToStrategies = (params: NewToStrategiesParams) => http.post('/api/v3/web/collaboration/to-strategies/', params);

/**
 * 跨租户协同-更新协同策略
 */
export const putToStrategies = (id: number, params: NewToStrategiesParams) => http.put(`/api/v3/web/collaboration/to-strategies/${id}/`, params);

/**
 * 跨租户协同-删除协同策略
 */
export const deleteToStrategies = (id: number) => http.delete(`/api/v3/web/collaboration/to-strategies/${id}/`);

/**
 * 跨租户协同-我接受的协同策略
 */
export const getFromStrategies = () => http.get('/api/v3/web/collaboration/from-strategies/');

/**
 * 跨租户协同-我接受的协同策略切换状态
 */
export const putFromStrategiesStatus = (id: number) => http.put(`/api/v3/web/collaboration/from-strategies/${id}/target-status/`);

/**
 * 跨租户协同-源租户自定义字段
 */
export const getSourceTenantCustomFields = (id: number) => http.get(`/api/v3/web/collaboration/from-strategies/${id}/source-tenant-custom-fields/`);

/**
 * 跨租户协同-确认协同策略
 */
export const putFromStrategiesConfirm = (params: FromStrategiesConfirmParams) => http.put(`/api/v3/web/collaboration/from-strategies/${params.id}/operations/confirm/`, params);

/**
 * 跨租户协同-编辑协同策略
 */
export const putFromStrategies = (params: FromStrategiesConfirmParams) => http.put(`/api/v3/web/collaboration/from-strategies/${params.id}/`, params);

/**
 * 跨租户协同-数据更新记录
 */
export const getCollaborationSyncRecords = (params: CollaborationSyncRecordsParams) => http.get('/api/v3/web/collaboration/sync-records/', params);
/**
 * 跨租户协同-数据更新记录-日志详情
 */
export const getCollaborationSyncRecordsLogs = (id: number) => http.get(`/api/v3/web/collaboration/sync-records/${id}/`);

/**
 * 跨租户协同-新建协同策略-目标租户
 */
export const getTenantList = (params: TenantItem) => http.get('/api/v3/web/collaboration/target-tenants/', params);
