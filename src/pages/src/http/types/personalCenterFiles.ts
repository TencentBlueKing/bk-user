/**
 * 租户用户更新邮箱
 */
export interface PatchUserEmailParams {
  id: string,
  is_inherited_email: boolean,
  custom_email: string,
  verification_code?: string,
}

/**
 * 租户用户更新手机号
 */
export interface PatchUserPhoneParams {
  id: string,
  is_inherited_phone: boolean,
  custom_phone: string,
  custom_phone_country_code: string,
  verification_code?: string,
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

/**
 * 租户修改手机号时，发送验证码
 */
export interface postPersonalCenterUserPhoneCaptchaParams {
  phone: string,
  phone_country_code?: string,
}

/**
 * 租户修改邮箱时，发送验证码
 */
export interface postPersonalCenterUserEmailCaptchaParams {
  email: string,
}

/**
 * 关联账户列表数据
 */
export interface CurrentNaturalUserData {
  id: string
  full_name: string
  tenant_users: {
    id: string
    username: string
    full_name: string
    logo: string
    tenant: {
      id: string
      name: string
    }
  }[]
}
export interface PersonalCenterUsersData {
  id: string
  username: string
  full_name: string
  logo: string
  is_inherited_email: boolean
  email: string
  custom_email: string
  is_inherited_phone: boolean
  phone: string
  phone_country_code: string
  custom_phone: string
  custom_phone_country_code: string
  account_expired_at: string
  departments: {
    id: number
    name: string
  }[]
  leaders: {
    id: string
    username: string
    full_name: string
  }[]
  extras?: Record<string, any>
  language: string
  time_zone: string
}

export interface PersonalCenterUserVisibleFieldsData {
  builtin_fields: {
    id: number
    name: string
    display_name: string
    data_type: string
    required: boolean
    unique: boolean
    default: string
    options: {
      id: string
      value: string
    }[]
  }[]
  custom_fields: {
    id: number
    name: string
    display_name: string
    data_type: string
    required: boolean
    editable: boolean
    options: {
      id: string
      value: string
    }[]
  }[]
}

export interface PersonalCenterUserFeatureData {
  can_change_password: boolean
  phone_update_restriction: string
  email_update_restriction: string
}
