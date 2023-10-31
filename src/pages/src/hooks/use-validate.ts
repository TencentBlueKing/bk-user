export default () => {
  const required = {
    required: true,
    message: '必填项',
    trigger: ['blur', 'change'],
  };

  const name = {
    validator: (value: string) => value.length && value.length <= 32,
    message: '由1-32位字符组成',
    trigger: 'blur',
  };

  const id = {
    validator: (value: string) => /^([a-zA-Z])([a-zA-Z0-9-]){2,31}$/.test(value),
    message: '由3-32位字母、数字、连接符(-)字符组成，以字母开头',
    trigger: 'blur',
  };

  const userName = {
    validator: (value: string) => /^([a-zA-Z0-9])([a-zA-Z0-9._-]){0,31}$/.test(value),
    message: '由1-32位字母、数字、下划线(_)、点(.)、减号(-)字符组成，以字母或数字开头',
    trigger: 'blur',
  };

  const email = {
    validator: (value: string) => /^([A-Za-z0-9_\-.])+@([A-Za-z0-9_\-.])+\.[A-Za-z]+$/.test(value),
    message: '请输入正确的邮箱地址',
    trigger: 'blur',
  };

  const phone = {
    validator: (value: string) => /^1[3-9]\d{9}$/.test(value),
    message: '请输入正确的手机号码',
    trigger: 'blur',
  };

  const fieldsDisplayName = {
    validator: (value: string) => {
      const nameLength = getByteLen(value);
      return nameLength <= 12;
    },
    message: '最多不得超过12个字符（6个汉字）',
    trigger: 'blur',
  };

  const fieldsName = {
    validator: (value: string) => /^[a-zA-Z]+$/.test(value),
    message: '由英文字母组成',
    trigger: 'blur',
  };

  const serverBaseUrl = {
    validator: (value: string) => /^https?:\/\/[a-zA-Z0-9-\\.]+(:\d+)?$/.test(value),
    message: '请输入正确的地址',
    trigger: 'blur',
  };

  const apiPath = {
    validator: (value: string) => /^\/[\w-]+(\/[\w-]+)*\/?$/.test(value),
    message: '请输入正确的 API 路径',
    trigger: 'blur',
  };

  const getByteLen = (str: string) => {
    // 匹配所有的中文
    const reg = /[\u4E00-\u9FA5]/;
    let len = 0;
    // 去掉前后空格
    str = str.replace(/(^\s+)|(\s+$)/g, '').replace(/\s/g, '');
    len += Array.from(str).reduce((total, char) => total + (reg.test(char) ? 2 : 1), 0);
    return len;
  };

  return {
    required,
    name,
    id,
    userName,
    email,
    phone,
    fieldsDisplayName,
    fieldsName,
    serverBaseUrl,
    apiPath,
  };
};
