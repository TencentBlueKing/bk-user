import Cookies from 'js-cookie';
import { createI18n } from 'vue-i18n';

import en from './en.json';
import zh from './zh.json';

let localLanguage = 'zh-cn';
const bluekingLanguage = Cookies.get('blueking_language');
if (bluekingLanguage && bluekingLanguage.toLowerCase() === 'en') {
  localLanguage = 'en';
}
const i18n = createI18n({
  legacy: false,
  locale: localLanguage,
  messages: {
    en,
    'zh-cn': zh,
  },
  silentTranslationWarn: true,
});

/** 默认语言选项 */
export const DEFAULT_LANGUAGE_OPTIONS = [
  { value: 'zh-cn', label: '简体中文' },
  { value: 'en', label: 'English' },
];

/** 动态加载语言包并通过 setLocaleMessage 设置到 i18n 实例 */
export async function loadMessages(langKey: string): Promise<boolean> {
  const prefix = '[bk-login][i18n]';
  try {
    console.log(`${prefix} 开始加载语言包 langKey=${langKey}`);
    const res = await fetch(`/login/staticfiles/${langKey}.json`);
    console.log(`${prefix} fetch 响应 langKey=${langKey} status=${res.status} ok=${res.ok}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const messages = await res.json();
    console.log(`${prefix} 解析 JSON 成功 langKey=${langKey}`);
    i18n.global.setLocaleMessage(langKey, messages);
    console.log(`${prefix} i18n locale message 已设置 langKey=${langKey}`);
    return true;
  } catch (err) {
    console.warn(`${prefix} 加载失败 langKey=${langKey}`, err);
    return false;
  }
}

export const { t, locale } = i18n.global;

export default i18n;
