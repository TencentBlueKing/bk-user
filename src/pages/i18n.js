const { resolve } = require('path');
const fs = require('fs');
const { extractI18NReport, readVueFiles, extractI18NItemsFromVueFiles, readLanguageFiles } = require('vue-i18n-extract');
const Dot = require('dot-object');

const dot = new Dot('.');
const config = {
  filePath: './src/**/*.?(js|vue|ts|tsx|jsx|html)',
  i18nPath: './src/language/**/*.?(json)'
}

const vueFiles = readVueFiles(resolve(process.cwd(), config.filePath));
const I18NItems = extractI18NItemsFromVueFiles(vueFiles);

const languageFiles = readLanguageFiles(resolve(process.cwd(), config.i18nPath));
const I18NLanguage = languageFiles.reduce((pre, item) => {
  const content = JSON.parse(item.content)
  const flatContent = dot.dot(content);
  // const lang = item.fileName.replace(/^.*[\\\/]/, '')
  pre[item.fileName] = Object.keys(flatContent).map(key => ({
    file: item.fileName,
    path: key
  }))
  return pre
}, {});

const report = extractI18NReport(I18NItems, I18NLanguage);

// 添加未翻译文案
languageFiles.forEach(languageFile => {
  const content = JSON.parse(languageFile.content);
  report.missingKeys.forEach(item => {
    if (item.language !== languageFile.fileName) return
    
    const defaultValue = languageFile.fileName.indexOf('zh') > -1 ? item.path : ''
    dot.str(item.path, defaultValue, content)
  })
  languageFile.content = JSON.stringify(content) // 保留结果

  fs.writeFileSync(languageFile.path, JSON.stringify(content, null, 2))
});
// 删除未使用文案
languageFiles.forEach(languageFile => {
  const content = JSON.parse(languageFile.content);
  report.unusedKeys.forEach(item => {
    if (item.language !== languageFile.fileName) return
    
    dot.delete(item.path, content)
  })
  languageFile.content = JSON.stringify(content) // 保留结果
  fs.writeFileSync(languageFile.path, JSON.stringify(content, null, 2))
});