import http from './fetch';
import type {
  DataSourceUsersParams,
  DataSourceUsersResult,
  DepartmentsParams,
  GeneratePasswordParams,
  LeadersParams,
  NewDataSourceParams,
  NewDataSourceUserParams,
  PutDataSourceParams,
  PutDataSourceUserParams,
  ResetPasswordParams,
  SyncRecordsParams,
  TestConnectionParams,
} from './types/dataSourceFiles';

/**
 * 数据源用户信息列表
 */
export const getDataSourceUsers = (params: DataSourceUsersParams): Promise<DataSourceUsersResult> => {
  const { id, username, page, pageSize } = params;
  return http.get(`/api/v1/web/data-sources/${id}/users/?username=${username}&page=${page}&page_size=${pageSize}`);
};

/**
 * 新建数据源用户
 */
export const newDataSourceUser = (params: NewDataSourceUserParams) => http.post(`/api/v1/web/data-sources/${params.id}/users/`, params);

/**
 * 数据源创建用户-下拉部门列表
 */
export const getDataSourceDepartments = (params: DepartmentsParams) => {
  const { id, name, page, pageSize } = params;
  return http.get(`/api/v1/web/data-sources/${id}/departments/?name=${name}&page=${page}&page_size=${pageSize}`);
};

/**
 * 数据源创建用户-下拉上级列表
 */
export const getDataSourceLeaders = (params: LeadersParams) => {
  const { id, keyword, page, pageSize } = params;
  return http.get(`/api/v1/web/data-sources/${id}/leaders/?keyword=${keyword}&page=${page}&page_size=${pageSize}`);
};

/**
 * 数据源用户详情
 */
export const getDataSourceUserDetails = (id: string) => http.get(`/api/v1/web/data-sources/users/${id}/`);

/**
 * 更新数据源用户
 */
export const putDataSourceUserDetails = (params: PutDataSourceUserParams) => http.put(`/api/v1/web/data-sources/users/${params.id}/`, params);

/**
 * 数据源列表
 */
export const getDataSourceList = (params: { type: string }) => http.get('/api/v1/web/data-sources/', params);

/**
 * 数据源插件列表
 */
export const getDataSourcePlugins = () => http.get('/api/v1/web/data-sources/plugins/');

/**
 * 新建数据源
 */
export const newDataSource = (params: NewDataSourceParams) => http.post('/api/v1/web/data-sources/', params);

/**
 * 数据源详情
 */
export const getDataSourceDetails = (id: string) => http.get(`/api/v1/web/data-sources/${id}/`);

/**
 * 新建数据源默认配置
 */
export const getDefaultConfig = (id: string) => http.get(`/api/v1/web/data-sources/plugins/${id}/default-config/`);

/**
 * 更新数据源
 */
export const putDataSourceDetails = (params: PutDataSourceParams) => http.put(`/api/v1/web/data-sources/${params.id}/`, params);

/**
 * 变更数据源状态
 */
export const changeSwitchStatus = (id: string) => http.patch(`/api/v1/web/data-sources/${id}/operations/switch_status/`);

/**
 * 数据源连通性测试
 */
export const postTestConnection = (params: TestConnectionParams) => http.post('/api/v1/web/data-sources/test-connection/', params);

/**
 * 数据源同步
 */
export const postOperationsSync = (id: string) => http.post(`/api/v1/web/data-sources/${id}/operations/sync/`);

/**
 * 生成数据源用户随机密码
 */
export const randomPasswords = (params: GeneratePasswordParams) => http.post('/api/v1/web/data-sources/random-passwords/', params);

/**
 * 数据源更新记录
 */
export const getSyncRecords = (params: SyncRecordsParams) => http.get(`/api/v1/web/data-sources/${params.id}/sync-records/`, params);

/**
 * 数据源更新日志
 */
export const getSyncLogs = (id: string) => http.get(`/api/v1/web/data-sources/sync-records/${id}/`);

/**
 * 重置数据源用户密码
 */
export const putUsersPassword = (params: ResetPasswordParams) => http.put(`/api/v1/web/data-sources/users/${params.id}/password/`, params);

/**
 * 重置数据源
 */
export const deleteDataSources = (id: string) => http.delete(`/api/v1/web/data-sources/${id}/`);

/**
 * 数据源关联资源信息
 */
export const getRelatedResource = (id: string) => http.get(`/api/v1/web/data-sources/${id}/related-resource-statistics/`);
