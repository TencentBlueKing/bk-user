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
              @click="() => handleSendCaptchaEmail(verifyFormRef, userId, verifyForm)">
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

import { useValidate } from '@/hooks';
import { useVerifyDialog } from '@/hooks/useVerifyDialog';
import { patchUsersEmail } from '@/http/personalCenterFiles';
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
const {
  captchaMessage,
  verifyFormCaptchaBtn,
  closeTimePolling,
  captchaValidate,
  verifySuccessText,
  verifySuccessVisible,
  transformTips,
  clearCaptchaMessage,
  clearCaptchaValidate,
  handleSendCaptchaEmail,
} = useVerifyDialog();

interface VerifyForm {
  email: string,
  captcha: string,
};
const verifyFormRef = ref(null);
const validate = useValidate();
const verifyFormRules = {
  email: [validate.required, validate.email],
  captcha: [validate.required],
};
const verifyForm = reactive<VerifyForm>({
  email: '',
  captcha: '',
});

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
const handleSubmitVerifyForm = async () => {
  captchaValidate.value = false;
  clearCaptchaMessage();
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
