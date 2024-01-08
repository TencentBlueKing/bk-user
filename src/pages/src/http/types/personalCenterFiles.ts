/**
 * 租户用户更新邮箱
 */
export interface PatchUserEmailParams {
  id: string,
  is_inherited_email: boolean,
  custom_email: string,
}

/**
 * 租户用户更新手机号
 */
export interface PatchUserPhoneParams {
  id: string,
  is_inherited_phone: boolean,
  custom_phone: string,
  custom_phone_country_code: string,
}

/**
 * 租户用户更新头像
 */
export interface PatchUserLogoParams {
  id: string,
  logo: string,
}

/**
 * 租户用户更新密码
 */
export interface PutUserPasswordParams {
  id: string,
  old_password: string,
  new_password: string,
}
