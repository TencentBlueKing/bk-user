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

// export const getUser = () => fetch.get(`${apiPrefix}/user`);

// 查询租户是否可见
export const getVisible = () => fetch.get(`${apiPrefix}/tenant-global-settings/`);

// 查询单个租户信息
export const getTenant = (id: string) => fetch.get(`${apiPrefix}/tenants/${id}/`);

// 查询多个租户信息
export const getTenantList = (ids: string) => fetch.get(`${apiPrefix}/tenants/?tenant_ids=${ids}`);

// 查询所有租户信息
export const getAllTenantList = () => fetch.get(`${apiPrefix}/tenants/`);

// 选择租户后要调用此接口确认登录
export const signIn = (params: SignInParams) => fetch.post(`${apiPrefix}/sign-in-tenants/`, params);

// 通过租户ID查询对应的登录方式
export const getIdpList = () => fetch.get(`${apiPrefix}/idps/`);

// 帐密登录
export const signInByPassword = (idpId: string, params: PasswordParams) => fetch
  .post(`${apiPrefix}/auth/idps/${idpId}/actions/authenticate/`, params);

// 账号列表
export const getUserList = () => fetch.get(`${apiPrefix}/tenant-users/`);

// 登录账号
export const signInByUser = (params: UserParams) => fetch.post(`${apiPrefix}/sign-in-users/`, params);
