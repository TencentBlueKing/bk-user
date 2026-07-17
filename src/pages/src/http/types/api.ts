import type { RoleType } from '@/common/constant';

export interface CurrentUser {
  username: string;
  display_name: string;
  role: RoleType;
  tenant_id: string;
  time_zone: string;
  language: string;
}

/** 语言代码类型，必定包含 'zh-cn' 和 'en'，同时允许其他语言代码 */
export type LanguageCode = 'zh-cn' | 'en' | string;

/** 支持的语言项 */
export interface SupportedLanguage {
  code: LanguageCode;
  name: string;
}
