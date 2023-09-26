interface ILoginData {
  loginUrl?: string
}
// 获取登录地址
const getLoginUrl = (url: string, cUrl: string) => {
  const loginUrl = new URL(url);
  loginUrl.searchParams.append('c_url', cUrl);
  return loginUrl.href;
};

// 登录
export const login = (data: ILoginData = {}) => {
  location.href = data.loginUrl || getLoginUrl(process.env.BK_LOGIN_URL, location.origin);
};

// 退出登录
export const logout = () => {
  location.href = getLoginUrl(process.env.BK_LOGIN_URL, location.origin);
};
