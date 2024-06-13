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

// 租户列表
export const getTenantList = payload => fetch.get(`${apiPrefix}/tenants/`, payload);

// 认证源列表
export const getIdpList = (id: string, userId: string) => fetch.get(`${apiPrefix}/tenants/${id}/idp-owner-tenants/${userId}/idps/`);

// 帐密登录
export const signInByPassword = (id: string, idpId: string, params: PasswordParams) => fetch
  .post(`${apiPrefix}/tenants/${id}/idps/${idpId}/actions/authenticate/`, params);
