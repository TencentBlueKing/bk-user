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

export const { t, locale } = i18n.global;

export default i18n;
