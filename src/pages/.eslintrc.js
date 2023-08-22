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
  },
  parserOptions: {
    project: 'tsconfig.eslint.json',
    tsconfigRootDir: __dirname,
  },
};
