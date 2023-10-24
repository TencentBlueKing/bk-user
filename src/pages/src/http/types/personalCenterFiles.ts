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
