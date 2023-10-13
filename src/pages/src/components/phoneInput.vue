<template>
  <div class="input-text">
    <input
      type="text"
      ref="telRef"
      :class="['select-text', { 'input-error': telError }]"
      v-model="data.phone"
      placeholder="请输入"
      @blur="verifyInput"
      @focus="hiddenVerify"
    />
    <p class="error-text" v-show="telError && data.phone">
      请填写正确的手机号
    </p>
    <p class="error-text" v-show="telError && !data.phone">
      必填项
    </p>
  </div>
</template>

<script setup lang="ts">
import intlTelInput from 'intl-tel-input/build/js/intlTelInput.min';
import telUtils from 'intl-tel-input/build/js/utils';
import { defineProps, onBeforeUnmount, onMounted, ref } from 'vue';

import { COUNTRY_CODE } from '@/utils';

const props = defineProps({
  formData: {
    type: Object,
    default: () => {},
  },
  telError: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['changeCountryCode', 'changeTelError']);

const data = ref(props.formData);
const telRef = ref();
const area = ref('cn');
const iti = ref(null);

onMounted(async () => {
  if (props.formData?.phone_country_code) {
    COUNTRY_CODE.forEach((item) => {
      if (item.tel === props.formData.phone_country_code) {
        area.value = item.short.toLowerCase();;
      }
    });
  }
  initIntlTel();
});

onBeforeUnmount(() => {
  iti?.value.destroy();
});

const initIntlTel = () => {
  const input = telRef.value;
  try {
    iti.value = intlTelInput(input, {
      allowDropdown: true,
      separateDialCode: true, // 国旗右边显示区号
      formatOnDisplay: false, // 不自动加空格或横线
      placeholderNumberType: 'MOBILE', // 手机号码
      initialCountry: area.value, // 初始国家
      preferredCountries: ['cn', 'us', 'gb'], // 偏好国家 中美英
      utilsScript: telUtils,
    });
  } catch (e) {
    console.warn('手机号国际化初始化失败，默认改为中国', e);
    handleInitError();
  }
  input.addEventListener('countrychange', () => {
    const countryData = iti.value.getSelectedCountryData(); // iso2(eg: cn) dialCode(eg: 86)
    area.value = countryData.iso2;
    emit('changeCountryCode', countryData.dialCode);
  });
};

const handleInitError = () => {
  const input = telRef.value;
  area.value = 'cn';
  iti.value = intlTelInput(input, {
    allowDropdown: true,
    separateDialCode: true, // 国旗右边显示区号
    formatOnDisplay: false, // 不自动加空格或横线
    placeholderNumberType: 'MOBILE', // 手机号码
    initialCountry: 'cn', // 初始国家
    preferredCountries: ['cn', 'us', 'gb'], // 偏好国家 中美英
    utilsScript: telUtils,
  });
};

const verifyInput = () => {
  if (data.value.phone === '') {
    return emit('changeTelError', true);
  }
  const validation = area.value === 'cn'
    ? /^1[3-9]\d{9}$/.test(data.value.phone)
    : iti.value.isValidNumber();
  !validation && (emit('changeTelError', true));
};

const hiddenVerify = () => {
  emit('changeTelError', false);
  window.changeInput = true;
};
</script>

<style lang="less">
@import url("@/css/intlTelInput.less");
</style>

<style lang="less" scoped>
.input-text {
  position: relative;
}

input::placeholder {
  color: #c4c6cc;
}

.select-text {
  width: 100%;
  height: 32px;
  line-height: 32px;
  color: #63656e;
  border: 1px solid #c4c6cc;
  border-radius: 2px;
  outline: none;
  resize: none;
}

.error-text {
  margin: 2px 0 0;
  font-size: 12px;
  line-height: 18px;
  color: #ea3636;
}

.input-error {
  border: 1px solid #ff5656;
}
</style>
