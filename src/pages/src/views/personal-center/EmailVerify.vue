<template>
  <bk-dialog
    v-model:is-show="isShow"
    render-directive="if"
    :close-icon="false"
    :quick-close="false">
    <template #header>
      <div class="mt-[24px] ml-[16px]">
        <span class="font-black text-[32px]">{{ t('邮箱验证') }}</span>
      </div>
    </template>
    <template #default>
      <bk-form
        :model="verifyForm"
        ref="verifyFormRef"
        :rules="verifyFormRules"
        form-type="vertical"
        class="ml-[16px] mr-[16px]">
        <bk-form-item
          class="mt-[32px]"
          property="email">
          <bk-input
            class="!w-[400px] !h-[40px]"
            :placeholder="t('请输入邮箱以接收邮箱验证码')"
            v-model="verifyForm.email">
          </bk-input>
        </bk-form-item>
        <bk-form-item
          class="mt-[24px] !mb-[0px]"
          property="captcha">
          <div class="flex justify-center">
            <bk-input
              :class="`!w-[400px] !h-[40px] ${captchaValidate ? 'captcha-input-validate' : ''}`"
              :placeholder="t('请输入验证码')"
              @blur="() => captchaValidate = false"
              @input="() => captchaValidate = false"
              v-model="verifyForm.captcha" />
            <bk-button
              outline theme="primary"
              class="!w-[141.68px] ml-[12px] !h-[40px]"
              :disabled="verifyFormCaptchaBtn.disabled"
              @click="handleSendCaptcha">
              {{ verifyFormCaptchaBtn.disabled ?
                `${verifyFormCaptchaBtn.times}s`
                : t('获取验证码') }}
            </bk-button>
          </div>
          <bk-overflow-title
            v-if="captchaValidate"
            class="captcha-error-text"
            type="tips">
            {{ captchaMessage }}
          </bk-overflow-title>
        </bk-form-item>
      </bk-form>
    </template>
    <template #footer>
      <div class="pb-[20px] ml-[16px] mb-[0px] w-[400px]">
        <bk-button
          class="mb-[10px] block h-[40px] w-[100%]" theme="primary" size="large" width="100%"
          :loading="submitBtnLoading"
          @click="handleSubmitVerifyForm">
          {{ t('确定') }}
        </bk-button>
        <bk-button class="h-[40px] w-[100%]" size="large" @click="handleCloseVerifyDialog">{{ t('取消') }}</bk-button>
      </div>
    </template>
  </bk-dialog>
  <bk-dialog
    v-model:is-show="verifySuccessVisible"
    class="verify-success-dialog"
    :close-icon="false"
    :quick-close="false"
    :esc-close="false"
  >
    <div class="text-center mt-[-4.62px]">
      <div class="flex justify-center">
        <img :src="right" class="h-[131.25px] w-[131.25px] " />
      </div>
      <div
        class="bk-infobox-title !text-[24px] !mt-[33.37px] leading-[32px] text-[#313238] font-bold">
        {{ verifySuccessText }}
      </div>
    </div>
    <div class="flex justify-center mt-[32px] pb-[8px]">
      <bk-button
        theme="primary"
        class="!h-[40px] !w-[100px] justify-center !text-[16px] !leading-[24px]"
        @click="verifySuccessVisible = false">
        {{ t('确定') }}
      </bk-button>
    </div>
    <template #footer></template>
  </bk-dialog>
</template>

<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Message, overflowTitle } from 'bkui-vue';
import { defineEmits, defineModel, defineProps, PropType, reactive, ref, watch } from 'vue';

import { openDialogResult } from './openDialogType';

import { useCountDown, useValidate } from '@/hooks';
import { patchUsersEmail, postPersonalCenterUserEmailCaptcha } from '@/http/personalCenterFiles';
import right from '@/images/right.svg';
import { t } from '@/language/index';

interface VerifyData {
  email: string,
}

const props = defineProps({
  curEmailText: {
    type: String,
    default: '',
  },
  userId: {
    type: String,
  },
  initialData: {
    type: Object as PropType<VerifyData>,
  },
});

const emit = defineEmits(['confirmVerifyEmail']);
const isShow = defineModel<boolean>('isShow', { required: true });

interface VerifyForm {
  email: string,
  captcha: string,
};

const verifyFormCaptchaBtn = reactive({
  disabled: false,
  times: 0,
});

const captchaValidate = ref(false);
const captchaMessage = ref('');

const clearCaptchaValidate = () => {
  captchaValidate.value = false;
  captchaMessage.value = '';
};

const closeTimePolling = ref(null);
// 发送验证码
const handleSendCaptcha = async () => {
  const result = validate.email.validator(verifyForm.email);
  if (!result) return;
  clearCaptchaValidate();
  verifyFormRef.value.clearValidate();
  const captchaCoolingTime = 60;
  const shutDownPointTime = 0;
  const { closeTimePolling: countDownCloseTimePolling } = useCountDown({
    beforeStart: () => {
      (async () => {
        verifyFormCaptchaBtn.times = captchaCoolingTime;
        verifyFormCaptchaBtn.disabled = true;
        const { userId } = props;
        // 获取邮箱验证码
        try {
          await postPersonalCenterUserEmailCaptcha(userId, {
            email: verifyForm.email,
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

const verifyForm = reactive<VerifyForm>({
  email: '',
  captcha: '',
});
const verifyFormRef = ref(null);
const validate = useValidate();
const verifyFormRules = {
  email: [validate.required, validate.email],
  captcha: [validate.required],
};

const resetCustomForm = () => {
  verifyForm.email = '';
  verifyForm.captcha = '';
};

watch(isShow, (newShow) => {
  if (newShow) {
    verifyForm.email = props.initialData.email;
  }
});

const handleCloseVerifyDialog = () => {
  isShow.value = false;
  clearCaptchaValidate();
  resetCustomForm();
};

const submitBtnLoading = ref(false);
const verifySuccessVisible = ref(false);
const verifySuccessText = ref(null);
const handleSubmitVerifyForm = async () => {
  captchaValidate.value = false;
  captchaMessage.value = '';
  const result = await verifyFormRef.value?.validate().catch(() => false);
  if (!result) return;

  submitBtnLoading.value = true;
  const { success, fail } = openDialogResult;

  let verifyResult = success;
  try {
    await patchUsersEmail({
      id: props.userId,
      is_inherited_email: false,
      custom_email: verifyForm.email,
      verification_code: verifyForm.captcha,
    }, { globalError: false });
    verifySuccessText.value = t('邮箱验证成功');
    emit('confirmVerifyEmail', { custom_email: verifyForm.email });
  } catch (err: any) {
    const captchaTips = err.response.data?.error?.message;
    transformTips(captchaTips, 'verify');
    verifyResult = fail;
    captchaValidate.value = true;
  }
  submitBtnLoading.value = false;
  if (verifyResult === success) {
    verifySuccessVisible.value = true;
    handleCloseVerifyDialog();
    closeTimePolling.value?.();
  }
};

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

</script>

<style lang="less" scoped>

.captcha-input-validate {
  border: 1px solid #ea3636 !important;
}

.captcha-error-text {
  width: 70%;
  position: absolute;
  margin: 2px 0 0;
  font-size: 12px;
  line-height: 18px;
  color: #ea3636;
  animation: form-error-appear-animation .15s
}

::v-deep .bk-dialog-footer {
  border: none;
  background-color: #fff;
}

</style>
