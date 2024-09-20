// 获取登录地址
export const getLoginUrl = (isOpener = true) => {
  const successUrl = isOpener ? `${window.location.origin}${window.BK_STATIC_URL}/login_success.html` : window.location.href;
  const siteLoginUrl = window.BK_LOGIN_URL || '';
  if (!siteLoginUrl) {
    console.error('Login URL not configured!');
    return;
  }

  const [loginBaseUrl] = siteLoginUrl.split('?');
  const newUrl = loginBaseUrl.includes('login') ? `${loginBaseUrl}/` : `${loginBaseUrl}login/`;
  const loginUrl = `${newUrl}plain?size=small&c_url=${encodeURIComponent(successUrl)}`;
  return loginUrl;
};

// 退出登录
export const logout = () => {
  location.href = `${getLoginUrl(false)}&is_from_logout=1`;
};
