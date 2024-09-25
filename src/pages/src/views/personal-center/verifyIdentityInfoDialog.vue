<template>
  <bk-dialog
    v-model:is-show="isShow"
    render-directive="if"
    :close-icon="false"
    :quick-close="false">
    <template #header>
      <div class="mt-[24px] ml-[16px]">
        <span class="font-black text-[32px]">{{ dialogTitle }}</span>
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
          v-if="curFormItemList.includes(formItemPropName.customEmail)" property="email">
          <bk-input class="!w-[400px] !h-[40px]" :placeholder="t('请输入邮箱以接收邮箱验证码')" v-model="verifyForm.email">
          </bk-input>
        </bk-form-item>

        <bk-form-item
          class="mt-[32px] h-[40px]"
          property="custom_phone"
          v-if="curFormItemList.includes(formItemPropName.customPhone)">
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
          property="captcha"
          v-if="curFormItemList.includes(formItemPropName.captcha)">
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
              @click="handleSendCaptcha">
              {{ verifyFormCaptchaBtn.disabled ? `${verifyFormCaptchaBtn.times}s` : t('获取验证码') }}
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
import type { Props as BkInfoBoxConfig } from 'bkui-vue/lib/info-box/info-box';
import { computed, defineEmits, defineModel, defineProps, PropType, reactive, ref, watch } from 'vue';

import { formItemPropName, openDialogResult, OpenDialogType } from './openDialogType';

import phoneInput from '@/components/phoneInput.vue';
import { useCountDown, useValidate } from '@/hooks';
import { patchUsersEmail, patchUsersPhone, postPersonalCenterUserEmailCaptcha, postPersonalCenterUserPhoneCaptcha } from '@/http/personalCenterFiles';
import right from '@/images/right.svg';
import { t } from '@/language/index';

interface VerifyData {
  phone: string,
  email: string,
  phone_country_code: string
}
interface VerifyConfig {
  type: OpenDialogType,
  data: VerifyData
}

const props = defineProps({
  curEmailText: {
    type: String,
    default: '',
  },
  curPhoneText: {
    type: String,
    default: '',
  },
  userId: {
    type: String,
  },
  currentVerifyConfig: {
    type: Object as PropType<VerifyConfig>,
  },
});

const emit = defineEmits(['confirmVerifyEmail', 'confirmVerifyPhone']);
const isShow = defineModel<boolean>('isShow', { required: true });
const telError = ref(false);

const changeTelError = (value: boolean, phone: string) => {
  telError.value = value;
  verifyForm.custom_phone = phone;
};
const changeCountryCode = (code: string) => {
  verifyForm.custom_phone_country_code = code;
};

const dialogTitle = computed(() => (props.currentVerifyConfig.type === OpenDialogType.email ? t('邮箱验证') : t('手机号验证')));

const curFormItemList = computed(() => {
  let formItemList = Object.values({ ...formItemPropName });
  if (props.currentVerifyConfig.type === OpenDialogType.email) {
    formItemList = formItemList.filter(item => !item.includes(OpenDialogType.phone));
  }
  if (props.currentVerifyConfig.type === OpenDialogType.phone) {
    formItemList = formItemList.filter(item => !item.includes(OpenDialogType.email));
  }
  return formItemList;
});

interface VerifyForm {
  email: string,
  custom_phone: string,
  captcha: string,
  custom_phone_country_code: string
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

// 发送验证码
const handleSendCaptcha = async () => {
  if (props.currentVerifyConfig.type === OpenDialogType.email) {
    const result = validate.email.validator(verifyForm.email);
    if (!result) return;
  }
  if (props.currentVerifyConfig.type === OpenDialogType.phone) {
    if (telError.value) return;
  }
  clearCaptchaValidate();
  verifyFormRef.value.clearValidate();
  const captchaCoolingTime = 60;
  const shutDownPointTime = 0;
  const { closeTimePolling } = useCountDown({
    beforeStart: () => {
      (async () => {
        verifyFormCaptchaBtn.times = captchaCoolingTime;
        verifyFormCaptchaBtn.disabled = true;
        const { userId } = props;
        // 获取邮箱验证码
        if (props.currentVerifyConfig.type === OpenDialogType.email) {
          try {
            await postPersonalCenterUserEmailCaptcha(userId, {
              email: verifyForm.email,
            }, { globalError: false });
            Message({ theme: 'success', message: t('发送成功') });
          } catch (err: any) {
            captchaValidate.value = true;
            captchaMessage.value = err.response.data?.error?.message;
          }
        }
        // 获取手机验证码
        if (props.currentVerifyConfig.type === OpenDialogType.phone) {
          try {
            await postPersonalCenterUserPhoneCaptcha(userId, {
              phone: verifyForm.custom_phone,
              phone_country_code: verifyForm.custom_phone_country_code,
            }, { globalError: false });
            Message({ theme: 'success', message: t('发送成功') });
          } catch (err: any) {
            captchaValidate.value = true;
            captchaMessage.value = err.response.data?.error?.message;
          }
        }
      })();
    },
    intervalFn: () => verifyFormCaptchaBtn.times -= 1,
    beforeClose: () => verifyFormCaptchaBtn.disabled = false,
  });

  watch([() => verifyFormCaptchaBtn.times, isShow], ([curBtnTimes, curShow]) => {
    curBtnTimes === shutDownPointTime && closeTimePolling();
    !curShow && closeTimePolling();
  });
  return;
};

const verifyForm = reactive<VerifyForm>({
  email: '',
  custom_phone: '',
  custom_phone_country_code: '86',
  captcha: '',
});
const verifyFormRef = ref(null);
const validate = useValidate();
const verifyFormRules = {
  email: [validate.required, validate.email],
  custom_phone: [validate.required],
  captcha: [validate.required],
};

const resetCustomForm = () => {
  verifyForm.email = '';
  verifyForm.custom_phone = '';
  verifyForm.captcha = '';
  verifyForm.custom_phone_country_code = '86';
};

watch(isShow, (newShow) => {
  if (newShow) {
    verifyForm.email = props.currentVerifyConfig.data?.email;
    verifyForm.custom_phone = props.currentVerifyConfig.data?.phone;
    verifyForm.custom_phone_country_code = props.currentVerifyConfig.data?.phone_country_code;
  }
});

const handleCloseVerifyDialog = () => {
  isShow.value = false;
  telError.value = false;
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

  const { type } = props.currentVerifyConfig;
  const { email, phone } = OpenDialogType;
  const { success, fail } = openDialogResult;
  const infoBoxConfig: Partial<BkInfoBoxConfig> = {
    type: success,
    title: '',
    closeIcon: false,
  };
  if (type === email) {
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
      captchaMessage.value = err.response.data?.error?.message;
      infoBoxConfig.type = fail;
      captchaValidate.value = true;
    }
  }
  if (type === phone) {
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
      captchaMessage.value = err.response.data?.error?.message;
      infoBoxConfig.type = fail;
      captchaValidate.value = true;
    }
  }
  submitBtnLoading.value = false;
  if (infoBoxConfig.type === success) {
    verifySuccessVisible.value = true;
    handleCloseVerifyDialog();
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
