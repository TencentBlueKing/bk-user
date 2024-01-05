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
    <bk-form
      form-type="vertical"
      ref="formRef"
      :model="formData"
      :rules="rules">
      <bk-form-item label="新密码" property="password" required>
        <div style="display: flex;">
          <bk-input v-model="formData.password" />
          <bk-button outline theme="primary" class="ml-[8px]" @click="handleRandomPassword">随机生成</bk-button>
        </div>
      </bk-form-item>
    </bk-form>
  </bk-dialog>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { reactive, ref, watch } from 'vue';

import useValidate from '@/hooks/use-validate';
import { putUsersPassword, randomPasswords } from '@/http/dataSourceFiles';

const validate = useValidate();
const emit = defineEmits(['closed', 'changePassword']);
const props = defineProps({
  config: {
    type: Object,
    default: () => ({}),
  },
});

const formRef = ref();
const formData = reactive({
  password: '',
});
const isLoading = ref(false);

const rules = {
  name: [validate.required],
};

watch(() => props.config?.isShow, (value: boolean) => {
  if (value) {
    formData.password = '';
  }
});

const handleRandomPassword = async () => {
  try {
    const params = {
      data_source_id: Number(props.config?.dataSourceId),
      password_rule_config: {},
    };
    const passwordRes = await randomPasswords(params);
    formData.password = passwordRes.data.password;
  } catch (e) {
    console.warn(e);
  }
};

const confirm = async () => {
  try {
    await formRef.value.validate();
    isLoading.value = true;
    await putUsersPassword({
      id: props.config?.userId,
      password: formData.password,
    });
    emit('changePassword');
    Message({ theme: 'success', message: '重置密码成功' });
  } catch (e) {
    isLoading.value = false;
  } finally {
    isLoading.value = false;
  }
};
</script>

<style lang="less" scoped>
.dialog-reset-password {
  ::v-deep .bk-modal-content {
    min-height: 0;
  }
}
</style>
