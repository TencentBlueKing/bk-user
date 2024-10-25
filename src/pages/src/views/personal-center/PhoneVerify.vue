<template>
  <bk-dialog
    v-model:is-show="isShow"
    render-directive="if"
    :close-icon="false"
    :quick-close="false">
    <template #header>
      <div class="mt-[24px] ml-[16px]">
        <span class="font-black text-[32px]">{{ t('手机号验证') }}</span>
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
          class="mt-[32px] h-[40px]"
          property="custom_phone">
          <phoneInput
            class="!w-[400px] phone-input"
            :form-data="verifyForm"
            :tel-error="telError"
            @change-country-code="changeCountryCode"
            @change-tel-error="changeTelError"
            custom-tel-error-text="请输入正确的手机号格式"
            :custom="true" />
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
              v-model="verifyForm.captcha"
              property="captcha" />
            <bk-button
              outline theme="primary"
              class="!w-[141.68px] ml-[12px] !h-[40px]"
              :disabled="verifyFormCaptchaBtn.disabled"
              @click="() => handleSendCaptchaPhone(verifyFormRef, userId, verifyForm)">
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
import { overflowTitle } from 'bkui-vue';
import { defineEmits, defineModel, defineProps, PropType, reactive, ref, watch } from 'vue';

import { openDialogResult } from './openDialogType';

import phoneInput from '@/components/phoneInput.vue';
import { useValidate } from '@/hooks';
import { useVerifyDialog } from '@/hooks/useVerifyDialog';
import { patchUsersPhone } from '@/http/personalCenterFiles';
import right from '@/images/right.svg';
import { t } from '@/language/index';

interface VerifyData {
  phone: string,
  phone_country_code: string
}

const props = defineProps({
  curPhoneText: {
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

const emit = defineEmits(['confirmVerifyPhone']);
const isShow = defineModel<boolean>('isShow', { required: true });
const {
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
  handleSendCaptchaPhone,
} = useVerifyDialog();

const changeTelError = (value: boolean, phone: string) => {
  telError.value = value;
  verifyForm.custom_phone = phone;
};
const changeCountryCode = (code: string) => {
  verifyForm.custom_phone_country_code = code;
};

interface VerifyForm {
  custom_phone: string,
  captcha: string,
  custom_phone_country_code: string
}
const verifyForm = reactive<VerifyForm>({
  custom_phone: '',
  custom_phone_country_code: '86',
  captcha: '',
});
const verifyFormRef = ref(null);
const validate = useValidate();
const verifyFormRules = {
  custom_phone: [validate.required],
  captcha: [validate.required],
};

const resetCustomForm = () => {
  verifyForm.custom_phone = '';
  verifyForm.captcha = '';
  verifyForm.custom_phone_country_code = '86';
};

watch(isShow, (newShow) => {
  if (newShow) {
    verifyForm.custom_phone = props.initialData.phone;
    verifyForm.custom_phone_country_code = props.initialData.phone_country_code;
  }
});

const handleCloseVerifyDialog = () => {
  isShow.value = false;
  telError.value = false;
  clearCaptchaValidate();
  resetCustomForm();
};

const submitBtnLoading = ref(false);
const handleSubmitVerifyForm = async () => {
  captchaValidate.value = false;
  clearCaptchaMessage();
  const result = await verifyFormRef.value?.validate().catch(() => false);
  if (!result) return;
  if (telError.value) return;
  submitBtnLoading.value = true;
  const { success, fail } = openDialogResult;

  let verifyResult = success;
  try {
    await patchUsersPhone({
      id: props.userId,
      is_inherited_phone: false,
      custom_phone: verifyForm.custom_phone,
      custom_phone_country_code: verifyForm.custom_phone_country_code,
      verification_code: verifyForm.captcha,
    }, { globalError: false });
    verifySuccessText.value = t('手机号验证成功');
    emit('confirmVerifyPhone', {
      custom_phone: verifyForm.custom_phone,
      custom_phone_country_code: verifyForm.custom_phone_country_code,
    });
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

</script>

<style lang="less" scoped>

.phone-input {
  ::v-deep .iti {
    height: 40px;
    .iti__flag-container {
      height: 100%;
    }
    input {
      height: 100% !important;
    }
  }
}

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
