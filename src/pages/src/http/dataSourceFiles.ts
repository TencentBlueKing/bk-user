import http from './fetch';
import type {
  DataSourceUsersResult,
  NewDataSourceUsersParams,
} from './types/dataSourceFiles';

/**
 * 数据源用户信息列表
 */
export const getDataSourceUsers = (id: string): Promise<DataSourceUsersResult> => http.get(`/api/v1/web/data-sources/${id}/users/`);

/**
 * 新建数据源用户
 */
export const newDataSourceUsers = (params: NewDataSourceUsersParams) => http.post(`/api/v1/web/data-sources/${params.id}/users/`);

/**
 * 数据源创建用户-下拉部门列表
 */
export const getDataSourceDepartments = (id: string) => http.get(`/api/v1/web/data-sources/${id}/departments/`);
