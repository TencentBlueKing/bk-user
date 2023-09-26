import fetch from './fetch';

const apiPrefix = '';

interface SignInParams {
  tenant_id: string;
}

interface PasswordParams {
  username: string;
  password: string;
}

interface UserParams {
  user_id: string;
}

export const getUser = () => fetch.get(`${apiPrefix}/user`);

export const getVisible = () => fetch.get(`${apiPrefix}/tenant-global-settings/`);

export const getTenant = (id: string) => fetch.get(`${apiPrefix}/tenants/${id}`);

export const getTenantList = (ids: string) => fetch.get(`${apiPrefix}/tenants/?tenant_ids=${ids}`);

// 选择公司后要调用此接口确认登录
export const signIn = (params: SignInParams) => fetch.post(`${apiPrefix}/sign-in-tenants/`, params);

// 帐密登录
export const signInByPassword = (idpId: string, params: PasswordParams) => fetch
  .post(`${apiPrefix}/auth/idps/${idpId}/actions/authenticate/`, params);

// 账号列表
export const getUserList = () => fetch.get(`${apiPrefix}/tenant-users/`);

// 登录账号
export const signInByUser = (params: UserParams) => fetch.post(`${apiPrefix}/sign-in-users/`, params);
