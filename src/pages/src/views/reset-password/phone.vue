<template>
  <bk-form ref="formRef" form-type="vertical" :model="formData" :rules="rules">
    <bk-form-item style="margin-bottom: 12px;" property="phone">
      <phoneInput
        :form-data="formData"
        :tel-error="telError"
        :tooltips="true"
        :input-style="true"
        @changeCountryCode="changeCountryCode"
        @changeTelError="changeTelError" />
    </bk-form-item>

    <div style="display: flex; align-items: flex-start;">
      <bk-form-item style="margin-bottom: 32px;" property="verification_code" error-display-type="tooltips">
        <bk-input
          :class="['verification-code-input', { 'is-enter': isEnter }]"
          size="large"
          v-model="formData.verification_code"
          :placeholder="$t('请输入验证码')"
          :maxlength="8"
          @blur="handleBlur"
          @keypress="handleKeypress">
        </bk-input>
      </bk-form-item>
      <bk-button
        style="width: 108px; font-size: 14px;"
        outline
        theme="primary"
        size="large"
        :disabled="codeDisabled"
        @click="handleSendCode"
      >
        {{ btnText }}
      </bk-button>
    </div>
    <bk-form-item style="margin-bottom: 12px;">
      <bk-button
        style="width: 100%;"
        theme="primary"
        size="large"
        :disabled="nextDisabled"
        @click="handleNextStep"
      >
        {{ $t('下一步') }}
      </bk-button>
    </bk-form-item>
    <bk-form-item>
      <bk-button
        style="width: 100%;"
        size="large"
        @click="logout"
      >
        {{ $t('取消') }}
      </bk-button>
    </bk-form-item>
  </bk-form>
</template>

<script setup lang="ts">
import { defineProps, reactive, ref } from 'vue';

import { logout } from '@/common/auth';
import phoneInput from '@/components/phoneInput.vue';
import useValidate from '@/hooks/use-validate';
import { resetPasswordUrl, verificationCodes } from '@/http/resetPasswordFiles';
import { t } from '@/language/index';

const validate = useValidate();

const props = defineProps({
  tenantId: {
    type: String,
    default: '',
  },
});

const formRef = ref();
const formData = reactive({
  tenant_id: '',
  phone: '',
  phone_country_code: '86',
  verification_code: '',
});
const codeDisabled = ref(false);
const btnText = ref(t('获取验证码'));
const nextDisabled = ref(true);
const remainTime = ref(60);
const timer = ref(0);

const rules = ref({
  verification_code: [validate.verifyCode],
});

const telError = ref(false);
const changeTelError = async (value: boolean) => {
  telError.value = value;
  nextDisabled.value = value || (formData.verification_code.length !== 8);
};

const changeCountryCode = (code: string) => {
  formData.phone_country_code = code;
};

const handleSendCode = async () => {
  try {
    if (!telError.value && formData.phone) {
      await verificationCodes({
        tenant_id: props.tenantId,
        phone: formData.phone,
        phone_country_code: formData.phone_country_code,
      });
      // 验证码倒计时
      timer.value = setInterval(() => {
        remainTime.value = remainTime.value - 1;
        codeDisabled.value = true;
        btnText.value = `${remainTime.value}${t('秒后可重发')}`;
        if (remainTime.value === 0) {
          clearInterval(timer.value);
          codeDisabled.value = false;
          btnText.value = t('获取验证码');
        }
      }, 1000);
      remainTime.value = 60;
    } else {
      changeTelError(true);
    }
  } catch (e) {
    console.warn(e);
  }
};

const handleBlur = async () => {
  try {
    isEnter.value = false;
    if (formData.phone && !telError.value) {
      await formRef.value.validate();
      nextDisabled.value = false;
    }
  } catch (e) {
    nextDisabled.value = true;
  }
};

const isEnter = ref(false);
const handleKeypress = () => {
  isEnter.value = true;
};

const handleNextStep = async () => {
  try {
    const res = await resetPasswordUrl({
      tenant_id: props.tenantId,
      phone: formData.phone,
      phone_country_code: formData.phone_country_code,
      verification_code: formData.verification_code,
    });
    window.location.href = res.data.reset_password_url;
  } catch (e) {
    console.warn(e);
  }
};
</script>

<style scoped lang="less">
.login-btn {
  width: 100%;
  margin-top: 10px;
}

::v-deep .verification-code-input {
  width: 280px;
  margin-right: 8px;
  border: none;

  input {
    background: #F0F1F5;
    border-radius: 2px;
  }
}

::v-deep .is-error {
  .verification-code-input {
    border: 1px solid #ea3636 !important;
  }

  .is-enter {
    border: none !important;
  }
}

::v-deep .is-focused {
  box-shadow: none !important;
}

::v-deep .bk-form-error-tips {
  top: 12px;
  right: 16px;
}
</style>
