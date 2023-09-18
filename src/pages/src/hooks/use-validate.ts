export default () => {
  const required = {
    required: true,
    message: '必填项',
    trigger: 'blur',
  };

  const name = {
    validator: (value: string) => value.length <= 32,
    message: '不能多于32个字符',
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

  return {
    required,
    name,
    id,
    userName,
    email,
    phone,
  };
};
