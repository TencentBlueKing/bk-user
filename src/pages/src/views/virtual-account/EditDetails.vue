<template>
  <div class="operation-wrapper user-scroll-y">
    <bk-form
      class="operation-content"
      ref="formRef"
      form-type="vertical"
      :model="formData"
      :rules="rules">
      <bk-form-item v-if="formData.id" :label="$t('用户ID')" :min-width="280">
        <bk-input
          v-model="formData.id"
          disabled
        />
      </bk-form-item>
      <bk-form-item :label="$t('用户名')" property="username" required>
        <bk-input
          v-model="formData.username"
          :placeholder="validate.userName.message"
          :disabled="formData.id"
          @focus="handleChange"
        />
      </bk-form-item>
      <bk-form-item :label="$t('全名')" property="full_name" required>
        <bk-input
          v-model="formData.full_name"
          :placeholder="validate.name.message"
          @focus="handleChange"
        />
      </bk-form-item>
      <bk-form-item :label="$t('邮箱')" property="email">
        <bk-input
          v-model="formData.email"
          @focus="handleChange"
        />
      </bk-form-item>
      <bk-form-item :label="$t('手机号')">
        <PhoneInput
          :form-data="formData"
          :tel-error="telError"
          :required="false"
          @change-country-code="changeCountryCode"
          @change-tel-error="changeTelError" />
      </bk-form-item>
    </bk-form>
    <div class="footer">
      <bk-button theme="primary" @click="handleSubmit" :loading="isLoading">
        {{ $t('保存') }}
      </bk-button>
      <bk-button @click="emit('handleCancelEdit')">
        {{ $t('取消') }}
      </bk-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';

import PhoneInput from '@/components/phoneInput.vue';
import { useValidate } from '@/hooks';
import { newVirtualUsers, putVirtualUsers } from '@/http';
import { t } from '@/language/index';

const emit = defineEmits(['handleCancelEdit', 'updateUsers']);

const props = defineProps({
  detailsInfo: {
    type: Object,
    default: {},
  },
});

const validate = useValidate();
const formRef = ref();

const formData = reactive({
  ...props.detailsInfo,
});

const rules = {
  username: [validate.required, validate.userName],
  full_name: [validate.required, validate.name],
  email: [validate.emailNotRequired],
};

const isLoading = ref(false);

const changeCountryCode = (code: string) => {
  formData.phone_country_code = code;
};

const telError = ref(false);

const changeTelError = (value: boolean) => {
  telError.value = value;
};

const handleSubmit = async () => {
  try {
    await formRef.value.validate();
    if (telError.value) return;

    isLoading.value = true;
    if (formData.id) {
      await putVirtualUsers(formData.id, {
        full_name: formData.full_name,
        email: formData.email,
        phone: formData.phone,
        phone_country_code: formData.phone_country_code,
      });
      emit('updateUsers', t('更新成功'));
    } else {
      await newVirtualUsers(formData);
      emit('updateUsers', t('创建成功'));
    }
  } finally {
    isLoading.value = false;
  }
};

const handleChange = () => {
  window.changeInput = true;
};
</script>

<style lang="less" scoped>
.operation-wrapper {
  padding: 28px 40px;

  .footer {
    margin-top: 32px;

    .bk-button {
      width: 88px;
      margin-right: 8px;
    }
  }
}
</style>
