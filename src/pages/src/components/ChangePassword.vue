<template>
  <bk-dialog
    ext-cls="dialog-reset-password"
    :is-show="config.isShow"
    :title="config.title"
    theme="primary"
    :quick-close="false"
    :is-loading="isLoading"
    @closed="$emit('closed')"
    @confirm="confirm"
  >
    <bk-alert
      theme="info"
      :title="$t('密码修改成功后需要进行重新登录')"
      closable
      class="mb-[24px]"
    />
    <bk-form
      form-type="vertical"
      ref="formRef"
      :model="formData">
      <bk-form-item :label="$t('旧密码')" property="oldPassword" required>
        <passwordInput v-model="formData.oldPassword" @input="(val) => inputPassword('oldPassword', val)" />
      </bk-form-item>
      <bk-form-item :label="$t('新密码')" property="newPassword" required>
        <passwordInput v-model="formData.newPassword" @input="(val) => inputPassword('newPassword', val)" />
      </bk-form-item>
      <bk-form-item :label="$t('确认密码')" property="confirmPassword" required>
        <passwordInput
          :class="{ 'is-error': isError }"
          v-model="formData.confirmPassword"
          :value="formData.confirmPassword"
          @input="(val) => inputPassword('confirmPassword', val)" />
        <div class="bk-form-error" v-show="isError">{{ $t('两次输入的密码不一致，请重新输入') }}</div>
      </bk-form-item>
    </bk-form>
  </bk-dialog>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { reactive, ref, watch } from 'vue';

import { logout } from '@/common/auth';
import passwordInput from '@/components/passwordInput.vue';
import { putPersonalCenterUserPassword } from '@/http';
import { t } from '@/language/index';

const props = defineProps({
  config: {
    type: Object,
    default: () => ({}),
  },
});
const emit = defineEmits(['closed']);
const formRef = ref();
const formData = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
});
const isLoading = ref(false);
const isError = ref(false);

watch(() => props.config?.isShow, (value: boolean) => {
  if (value) {
    Object.keys(formData).forEach((key) => {
      formData[key] = '';
    });
    isError.value = false;
  }
});

const inputPassword = (param, val) => {
  formData[param] = val;
  if (param === 'confirmPassword') {
    isError.value = false;
  }
};

const confirm = async () => {
  try {
    await formRef.value.validate();
    if (formData.newPassword !== formData.confirmPassword) {
      return isError.value = true;
    }
    isLoading.value = true;
    await putPersonalCenterUserPassword({
      id: props.config?.id,
      old_password: formData.oldPassword,
      new_password: formData.newPassword,
    });
    emit('closed');
    Message({ theme: 'success', message: t('修改密码成功') });
    logout();
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style lang="less" scoped>
.dialog-reset-password {
  ::v-deep .bk-alert {
    margin: 5px 0 16px;
  }

  .is-error {
    border-color: #ea3636;
  }

  .error {
    position: absolute;
    padding-top: 4px;
    font-size: 12px;
    line-height: 1;
    color: #ea3636;
  }
}
:deep(.copy-icon) {
  right: 30px;
}
</style>
