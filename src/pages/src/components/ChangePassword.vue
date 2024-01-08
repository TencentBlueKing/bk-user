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
      title="密码修改成功后需要进行重新登录"
      closable
    />
    <bk-form
      form-type="vertical"
      ref="formRef"
      :model="formData">
      <bk-form-item label="旧密码" property="oldPassword" required>
        <bk-input v-model="formData.oldPassword" />
      </bk-form-item>
      <bk-form-item label="新密码" property="newPassword" required>
        <bk-input v-model="formData.newPassword" />
      </bk-form-item>
      <bk-form-item label="确认密码" property="confirmPassword" required>
        <bk-input :class="{ 'is-error': isError }" v-model="formData.confirmPassword" @input="changePassword" />
        <p class="error" v-show="isError">两次输入的密码不一致，请重新输入</p>
      </bk-form-item>
    </bk-form>
  </bk-dialog>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { reactive, ref, watch } from 'vue';

import { putPersonalCenterUserPassword } from '@/http/personalCenterFiles';

const emit = defineEmits(['closed']);
const props = defineProps({
  config: {
    type: Object,
    default: () => ({}),
  },
});

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

const changePassword = () => {
  isError.value = false;
};

const confirm = async () => {
  try {
    await formRef.value.validate();
    if (formData.newPassword === formData.confirmPassword) {
      return isError.value = true;
    }
    isLoading.value = true;
    await putPersonalCenterUserPassword({
      id: props.config?.id,
      old_password: formData.oldPassword,
      new_password: formData.newPassword,
    });
    emit('closed');
    Message({ theme: 'success', message: '修改密码成功' });
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
</style>
