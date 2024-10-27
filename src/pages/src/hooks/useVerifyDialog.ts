import { Message } from 'bkui-vue';
import { reactive, ref, watch } from 'vue';

import { useCountDown } from './useCountDown';
import { useValidate } from './useValidate';

import { postPersonalCenterUserEmailCaptcha, postPersonalCenterUserPhoneCaptcha } from '@/http';
import { t } from '@/language';

export const useVerifyDialog = () => {
  const telError = ref(false);
  const validate = useValidate();
  const captchaMessage = ref('');
  const closeTimePolling = ref(null);
  const captchaValidate = ref(false);
  const verifySuccessText = ref(null);
  const verifySuccessVisible = ref(false);
  const verifyFormCaptchaBtn = reactive({
    disabled: false,
    times: 0,
  });

  const transformTips = (currentTips: string, type: string) => {
    const CAPTCHA_ERROR_CN = '验证码无效: 验证码错误';
    const CAPTCHA_ERROR_EN = 'Invalid verification code: Incorrect verification code';
    const OVER_LIMIT_ERROR_CN = '发送验证码失败: 今日发送验证码次数超过上限，请明天再试';
    // eslint-disable-next-line @typescript-eslint/quotes
    const OVER_LIMIT_ERROR_EN = `Failed to send verification code: Today's limit for sending verification codes has been exceeded, please try again tomorrow`;
    let transformedMessage = currentTips;

    if (type === 'verify' && (currentTips === CAPTCHA_ERROR_CN || currentTips === CAPTCHA_ERROR_EN)) {
      transformedMessage = t('验证码错误，请重试');
    } else if (type === 'captcha' && (currentTips === OVER_LIMIT_ERROR_CN || currentTips === OVER_LIMIT_ERROR_EN)) {
      transformedMessage = t('发送验证码次数超过上限，请一天之后再试');
    }
    captchaMessage.value = transformedMessage;
  };

  const clearCaptchaMessage = () => {
    captchaMessage.value = '';
  };

  const clearCaptchaValidate = () => {
    captchaValidate.value = false;
    clearCaptchaMessage();
  };

  // 发送验证码
  const handleSendCaptchaEmail = async (formRef, userId, formData) => {
    const result = validate.email.validator(formData.email);
    if (!result) return;
    clearCaptchaValidate();
    formRef.clearValidate();
    const captchaCoolingTime = 60;
    const shutDownPointTime = 0;
    const { closeTimePolling: countDownCloseTimePolling } = useCountDown({
      beforeStart: () => {
        (async () => {
          verifyFormCaptchaBtn.times = captchaCoolingTime;
          verifyFormCaptchaBtn.disabled = true;
          // 获取邮箱验证码
          try {
            await postPersonalCenterUserEmailCaptcha(userId, {
              email: formData.email,
            }, { globalError: false });
            Message({ theme: 'success', message: t('发送成功') });
          } catch (err: any) {
            captchaValidate.value = true;
            const captchaTips = err.response.data?.error?.message;
            transformTips(captchaTips, 'captcha');
          }
        })();
      },
      intervalFn: () => verifyFormCaptchaBtn.times -= 1,
      beforeClose: () => verifyFormCaptchaBtn.disabled = false,
    });
    closeTimePolling.value = countDownCloseTimePolling;

    // 关闭dialog仍需保持倒计时
    watch(() => verifyFormCaptchaBtn.times, (curBtnTimes: number) => {
      curBtnTimes === shutDownPointTime && closeTimePolling.value();
    });
    return;
  };

  const handleSendCaptchaPhone = async (formRef, userId, formData) => {
    if (telError.value) return;
    clearCaptchaValidate();
    formRef.clearValidate();
    const captchaCoolingTime = 60;
    const shutDownPointTime = 0;
    const { closeTimePolling: countDownCloseTimePolling } = useCountDown({
      beforeStart: () => {
        (async () => {
          verifyFormCaptchaBtn.times = captchaCoolingTime;
          verifyFormCaptchaBtn.disabled = true;
          // 获取手机验证码
          try {
            await postPersonalCenterUserPhoneCaptcha(userId, {
              phone: formData.custom_phone,
              phone_country_code: formData.custom_phone_country_code,
            }, { globalError: false });
            Message({ theme: 'success', message: t('发送成功') });
          } catch (err: any) {
            captchaValidate.value = true;
            const captchaTips = err.response.data?.error?.message;
            transformTips(captchaTips, 'captcha');
          }
        })();
      },
      intervalFn: () => verifyFormCaptchaBtn.times -= 1,
      beforeClose: () => verifyFormCaptchaBtn.disabled = false,
    });
    closeTimePolling.value = countDownCloseTimePolling;
    // 关闭dialog仍需保持倒计时
    watch(() => verifyFormCaptchaBtn.times, (curBtnTimes) => {
      curBtnTimes === shutDownPointTime && closeTimePolling.value();
    });
    return;
  };

  return {
    captchaMessage,
    verifyFormCaptchaBtn,
    closeTimePolling,
    captchaValidate,
    verifySuccessText,
    verifySuccessVisible,
    telError,
    transformTips,
    clearCaptchaMessage,
    clearCaptchaValidate,
    handleSendCaptchaEmail,
    handleSendCaptchaPhone,
  };
};
