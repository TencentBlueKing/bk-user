<template>
  <div class="operation-wrapper user-scroll-y">
    <bk-form
      class="operation-content"
      ref="formRef"
      form-type="vertical"
      :model="formData"
      :rules="rules">
      <bk-form-item v-if="formData.id" :label="$t('账号ID')" :min-width="280">
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
          :placeholder="validate.fullName.message"
          @focus="handleChange"
        />
      </bk-form-item>
      <bk-form-item :label="$t('所属应用')" property="app_codes" required>
        <bk-input
          v-model="formData.app_codes"
          :placeholder="$t('请输入应用名，支持输入多个，以逗号进行区隔')"
          @focus="handleChange"
        />
      </bk-form-item>
      <bk-form-item :label="$t('账号责任人')" property="owners" required>
        <UserSelector v-model:value="formData.owners" />
      </bk-form-item>
    </bk-form>
    <div class="footer">
      <bk-button theme="primary" @click="handleSubmit" :loading="isLoading" :disabled="isDisabled">
        {{ formData.id ? $t('保存') : $t('创建账号') }}
      </bk-button>
      <bk-button @click="emit('handleCancelEdit')">
        {{ $t('取消') }}
      </bk-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import {  reactive, ref, watch } from 'vue';

import UserSelector from '@/components/UserSelector.vue';
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
const originalData = { ...props.detailsInfo };
const isDisabled = ref(true);

watch(formData, () => {
  isDisabled.value = originalData.id ? JSON.stringify(originalData) === JSON.stringify(formData) : false;
}, { deep: true, immediate: true });

const rules = {
  username: [validate.required, validate.userName],
  full_name: [validate.required, validate.fullName],
  app_codes: [validate.required],
  owners: [validate.required],
};

const isLoading = ref(false);

const handleSubmit = async () => {
  try {
    await formRef.value.validate();

    isLoading.value = true;
    if (formData.id) {
      await putVirtualUsers(formData.id, {
        full_name: formData.full_name,
        app_codes: formData.app_codes.split(','),
        owners: formData.owners,
      });
      emit('updateUsers', t('更新成功'));
    } else {
      await newVirtualUsers({
        username: formData.username,
        full_name: formData.full_name,
        owners: formData.owners,
        app_codes: formData.app_codes.split(','),
      });
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
