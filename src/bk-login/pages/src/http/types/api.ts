/**
 * 全局配置返回结果
 */
export interface GlobalSettingsResult {
  bk_user_url: string;
  unique_enabled_tenant_idp: string | null;
  supported_languages: SupportedLanguage[];
}

/** 语言代码类型，必定包含 'zh-cn' 和 'en'，同时允许其他语言代码 */
export type LanguageCode = 'zh-cn' | 'en' | string;

/** 支持的语言 */
export interface SupportedLanguage {
  /** 语言代码，必定包含 'zh-cn' 和 'en' */
  code: LanguageCode;
  /** 语言名称 */
  name: string;
}
