/**
 * 用户名
 * 由1-32位字母、数字、下划线(_)、点(.)、减号(-)字符组成，以字母或数字开头
 */
export const usernameRegex = {
  rule: /^([a-zA-Z])([a-zA-Z0-9._-]){0,31}$/,
  message: '由1-32位字母、数字、下划线(_)、点(.)、减号(-)字符组成，以字母或数字开头',
};

/**
 * 邮箱
 */
export const emailRegex = {
  rule: /^([A-Za-z0-9_\-.])+@([A-Za-z0-9_\-.])+\.[A-Za-z]+$/,
  message: '请输入正确的邮箱地址',
};

/**
 * 手机号
 */
export const telRegex = {
  rule: /^1[3-9]\d{9}$/,
  message: '请输入正确的手机号码',
};

/**
 * 租户ID
 */
export const tenantIdRegex = {
  rule: /^([a-zA-Z])([a-zA-Z0-9-]){2,31}$/,
  message: '由3-32位字母、数字、连接符(-)字符组成，以字母开头',
};
