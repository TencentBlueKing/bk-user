import { computed, ref, watch } from 'vue';

import { randomPasswords } from '@/http';


export const useAdminPassword = (formData) => {
  // 通知方式
  const emailError = ref(false);
  const telError = ref(false);

  const isEmail = computed(() => formData.notification_method === 'email');

  const changePassword = (val: string) => {
    formData.fixed_password = val;
    window.changeInput = true;
  };

  // 随机密码
  const handleRandomPassword = async () => {
    try {
      const passwordRes = await randomPasswords({});
      formData.fixed_password = passwordRes.data.password;
      window.changeInput = true;
    } catch (e) {
      console.warn(e);
    }
  };

  watch(() => formData.notification_method, (val) => {
    if (val === 'email') {
      formData.phone = '';
      formData.phone_country_code = '86';
      telError.value = false;
    } else {
      formData.email = '';
      emailError.value = false;
    }
  });

  const handleBlur = () => {
    const verify = /^([A-Za-z0-9_\-.])+@([A-Za-z0-9_\-.])+\.[A-Za-z]+$/.test(formData.email);
    if (formData.email === '' || !verify) {
      emailError.value = true;
    } else {
      emailError.value = false;
    }
  };

  const handleInput = () => {
    emailError.value = false;
  };

  const changeCountryCode = (code: string) => {
    formData.phone_country_code = code;
  };

  const changeTelError = (value: boolean) => {
    telError.value = value;
  };

  return {
    changePassword,
    handleRandomPassword,
    emailError,
    telError,
    isEmail,
    handleBlur,
    handleInput,
    changeCountryCode,
    changeTelError,
  };
};
