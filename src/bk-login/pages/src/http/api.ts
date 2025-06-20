import fetch from './fetch';

const apiPrefix = '';

interface PasswordParams {
  username: string;
  password: string;
}

interface UserParams {
  user_id: string;
}

// 账号列表
export const getUserList = () => fetch.get(`${apiPrefix}/tenant-users/`);

// 登录账号
export const signInByUser = (params: UserParams) => fetch.post(`${apiPrefix}/sign-in-users/`, params);

// 搜索租户列表，支持 id 和 name
export const getSearchTenantList = (payload: { keyword: string }) => fetch.get(`${apiPrefix}/tenants/-/search`, payload);

// 通过id搜索租户列表
export const getTenantList = (payload: { tenant_ids: string }) => fetch.get(`${apiPrefix}/tenants/`, payload);

// 认证源列表
export const getIdpList = (id: string) => fetch.get(`${apiPrefix}/idps/`, { tenant_id: id });

// 帐密登录
export const signInByPassword = (id: string, idpId: string, params: PasswordParams) => fetch
  .post(`${apiPrefix}/auth/idps/${idpId}/actions/authenticate/`, params);

// 管理员登录
export const signInByAdmin = (idpId: string, params: PasswordParams) => fetch
  .post(`${apiPrefix}/builtin-management-auth/idps/${idpId}/authenticate/`, params);

// 全局配置
export const getGlobalSettings = () => fetch.get(`${apiPrefix}/global-settings/`);
