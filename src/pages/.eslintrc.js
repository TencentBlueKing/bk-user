// 导入自定义规则中的 getRoleMapping 函数
const { getRoleMapping } = require('./eslint-rules/no-hardcoded-role-values');

// 获取角色值映射
const roleMapping = getRoleMapping();
const roleValues = Object.keys(roleMapping);

module.exports = {
  root: true,
  extends: ['@blueking/eslint-config-bk/tsvue3'],
  plugins: [
    'simple-import-sort',
  ],
  rules: {
    'simple-import-sort/imports': ['error', {
      groups: [
        ['^[a-zA-Z]'],
        ['^@\\w'],
        ['^\\.\\.'],
        ['^\\.'],
      ],
    }],
    'no-param-reassign': 'off',
    // 禁止在 <script> 中使用硬编码的角色值
    'no-restricted-syntax': [
      'warn',
      ...roleValues.map(value => ({
        selector: `Literal[value="${value}"]`,
        message: `不要使用硬编码的角色值 "${value}"，请使用 ROLE.${roleMapping[value]} 常量`,
      })),
    ],
    // 禁止在 <template> 中使用硬编码的角色值
    'vue/no-restricted-syntax': [
      'warn',
      ...roleValues.map(value => ({
        selector: `VLiteral[value="${value}"]`,
        message: `不要在模板中使用硬编码的角色值 "${value}"，请使用 ROLE.${roleMapping[value]} 常量`,
      })),
    ],
  },
  parserOptions: {
    project: 'tsconfig.eslint.json',
    tsconfigRootDir: __dirname,
  },
  overrides: [
    {
      // 允许配置文件和 eslint-rules 目录使用 CommonJS 的 require
      files: ['.eslintrc.js', 'eslint-rules/**/*.js'],
      rules: {
        '@typescript-eslint/no-require-imports': 'off',
      },
    },
  ],
};
