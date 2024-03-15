<template>
  <bk-form ref="formRef" form-type="vertical" :model="formData" :rules="rules">
    <bk-form-item property="email" style="margin-bottom: 32px;" error-display-type="tooltips">
      <bk-input
        :class="['email-input', { 'is-enter': isEnter }]"
        size="large"
        v-model="formData.email"
        :placeholder="$t('请输入邮箱地址')"
        @blur="handleBlur"
        @keypress="handleKeypress">
      </bk-input>
    </bk-form-item>
    <bk-form-item style="margin-bottom: 12px;">
      <bk-button
        style="width: 100%;"
        theme="primary"
        size="large"
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
import { reactive, ref } from 'vue';

import { logout } from '@/common/auth';
import useValidate from '@/hooks/use-validate';
import { tokenUrls } from '@/http/resetPasswordFiles';

const validate = useValidate();

const props = defineProps({
  tenantId: {
    type: String,
    default: '',
  },
});

const emit = defineEmits(['emailSend']);

const formRef = ref();
const formData = reactive({
  email: '',
});

const rules = ref({
  email: [validate.email],
});

const handleNextStep = async () => {
  try {
    await formRef.value.validate();
    await tokenUrls({
      tenant_id: props.tenantId,
      email: formData.email,
    });
    emit('emailSend', true, formData.email);
  } catch (e) {
    console.warn(e);
  }
};

const isEnter = ref(false);

const handleBlur = () => {
  isEnter.value = false;
};

const handleKeypress = () => {
  isEnter.value = true;
};
</script>

<style scoped lang="less">
.login-btn {
  width: 100%;
  margin-top: 10px;
}

.error-text {
  color: #ea3636;
  text-align: center;
}

::v-deep .email-input {
  border: none;

  input {
    background: #F0F1F5;
    border-radius: 2px;
  }
}

::v-deep .is-error {
  .email-input {
    border: 1px solid #ea3636 !important;
  }

  .is-enter {
    border: none !important;
  }
}

::v-deep .is-focused {
  box-shadow: none !important;
}
</style>
