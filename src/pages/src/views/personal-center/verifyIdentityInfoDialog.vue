<template>
  <bk-dialog
    v-model:is-show="isShow"
    render-directive="if"
    :close-icon="false"
    :quick-close="false">
    <template #header>
      <div class="pt-[20px] pl-[20px]">
        <span class="font-black text-[30px]">{{ dialogTitle }}</span>
        <div class="text-xs mt-[10px] text-[#8a8b92]">
          <slot name="header-tips"></slot>
        </div>
      </div>
    </template>
    <template #default>
      <bk-form :model="verifyForm" ref="verifyFormRef" :rules="verifyFormRules" form-type="vertical">
        <bk-form-item
          class="m-[10px] mt-[20px] !mb-[10px] h-[40px]"
          v-if="curFormItemList.includes(formItemPropName.customEmail)" property="email" required>
          <bk-input :placeholder="t('请输入邮箱以接收邮箱验证码')" v-model="verifyForm.email">
          </bk-input>
        </bk-form-item>

        <bk-form-item
          class="m-[10px] mt-[20px] !mb-[10px] h-[40px]"
          v-if="curFormItemList.includes(formItemPropName.customPhone)">
          <phoneInput
            :form-data="verifyForm"
            :tel-error="telError"
            @change-country-code="changeCountryCode"
            @change-tel-error="changeTelError"
            :custom="true" />
        </bk-form-item>

        <bk-form-item
          class="m-[10px] mt-[20px]"
          v-if="curFormItemList.includes(formItemPropName.captcha)">
          <div class="flex justify-center">
            <bk-input
              :placeholder="t('请输入验证码')"
              v-model="verifyForm.captcha"
              property="captcha" />
            <bk-button
              outline theme="primary" class="ml-[10px] w-[120px]"
              :disabled="verifyFormCaptchaBtn.disabled"
              @click="handleSendCaptcha">
              {{ verifyFormCaptchaBtn.disabled ? `${verifyFormCaptchaBtn.times}s` : t('获取验证码') }}
            </bk-button>
          </div>
        </bk-form-item>
      </bk-form>
    </template>
    <template #footer>
      <div class="pb-[20px] m-[10px] mb-[0px]">
        <bk-button
          class="w-[100%] mb-[10px] block" theme="primary" size="large" width="100%"
          :loading="submitBtnLoading"
          @click="handleSubmitVerifyForm">
          {{ t('确定') }}
        </bk-button>
        <bk-button class="w-[100%]" size="large" @click="handleCloseVerifyDialog">{{ t('取消') }}</bk-button>
      </div>
    </template>
  </bk-dialog>
</template>

<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { InfoBox, Message } from 'bkui-vue';
import type { Props as BkInfoBoxConfig } from 'bkui-vue/lib/info-box/info-box';
import { computed, defineModel, defineProps, PropType, reactive, ref, watch } from 'vue';

import { formItemPropName, openDialogResult, OpenDialogType } from './openDialogType';

import phoneInput from '@/components/phoneInput.vue';
import { useCountDown, useValidate } from '@/hooks';
import { postPersonalCenterUserEmailCaptcha, postPersonalCenterUserPhoneCaptcha } from '@/http/personalCenterFiles';
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

// 发送验证码
const handleSendCaptcha = async () => {
  if (props.currentVerifyConfig.type === OpenDialogType.email) {
    const result = await verifyFormRef.value.validate().catch(() => false);
    if (!result) return;
  }
  if (props.currentVerifyConfig.type === OpenDialogType.phone) {
    if (telError.value) return;
  }
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
          await postPersonalCenterUserEmailCaptcha(userId, {
            email: verifyForm.email,
          });
          Message({ theme: 'success', message: t('发送成功') });
        }
        // 获取手机验证码
        if (props.currentVerifyConfig.type === OpenDialogType.phone) {
          await postPersonalCenterUserPhoneCaptcha(userId, {
            phone: verifyForm.custom_phone,
            phone_country_code: verifyForm.custom_phone_country_code
          });
          Message({ theme: 'success', message: t('发送成功') });
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
  phone_country_code: '86',
  captcha: '',
});
const verifyFormRef = ref(null);
const validate = useValidate();
const verifyFormRules = {
  email: [validate.required, validate.email],
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
  resetCustomForm();
};

const submitBtnLoading = ref(false);
const handleSubmitVerifyForm = async () => {
  const result = await verifyFormRef.value?.validate().catch(() => false);
  if (!result) return;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { type } = props.currentVerifyConfig;
  const { email, phone } = OpenDialogType;
  const { success, fail } = openDialogResult;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  submitBtnLoading.value = true;
  const infoBoxConfig: Partial<BkInfoBoxConfig> = {
    type: success,
    title: '',
    closeIcon: false,
  };

  // if (type === email && active === custom)

  if (type === email && infoBoxConfig.type === success) infoBoxConfig.title = t('邮箱验证成功');
  if (type === email && infoBoxConfig.type === fail) infoBoxConfig.title = t('邮箱验证失败');
  if (type === phone && infoBoxConfig.type === success) infoBoxConfig.title = t('手机号验证成功');
  if (type === phone && infoBoxConfig.type === fail) infoBoxConfig.title = t('手机号验证失败');

  submitBtnLoading.value = false;
  // handleCloseVerifyDialog();
  // InfoBox(infoBoxConfig);
};

</script>

<style lang="less">
.verify-identity-info-tab-panel {
  margin-top: -10px;
  height: 170px;
  .bk-tab-header {
    justify-content: center;
  }
}

.verify-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  margin-right: 5px;
  vertical-align: middle;
}
</style>
