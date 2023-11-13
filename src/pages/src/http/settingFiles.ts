import http from './fetch';
import type {
  NewCustomFieldsParams,
  PutCustomFieldsParams,
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
export const getTenantSetting = () => http.get('/api/v1/web/tenant-setting/settings/tenant-user-validity-period/');

/**
 * 更新当前租户的账户有效期设置
 */
export const putTenantSetting = () => http.put('/api/v1/web/tenant-setting/settings/tenant-user-validity-period/');
