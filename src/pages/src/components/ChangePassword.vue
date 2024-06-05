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
        <bk-input :type="isOldPassword ? 'password' : 'text'" v-model="formData.oldPassword">
          <template #suffix>
            <span class="copy-icon">
              <i class="user-icon icon-copy text-[#3A84FF] text-[14px] " @click="copy(formData.oldPassword)" />
            </span>
            <span
              v-show="!isOldPassword"
              class="inline-flex text-[14px] ml-[8px] mr-[8px] text-[#c4c6cc] hover:text-[#313238]"
              @click="isOldPassword = true">
              <eye />
            </span>
          </template>
        </bk-input>
      </bk-form-item>
      <bk-form-item :label="$t('新密码')" property="newPassword" required>
        <bk-input :type="isNewPassword ? 'password' : 'text'" v-model="formData.newPassword">
          <template #suffix>
            <span class="copy-icon">
              <i class="user-icon icon-copy text-[#3A84FF] text-[14px] " @click="copy(formData.newPassword)" />
            </span>
            <span
              v-show="!isNewPassword"
              class="inline-flex text-[14px] ml-[8px] mr-[8px] text-[#c4c6cc] hover:text-[#313238]"
              @click="isNewPassword = true">
              <eye />
            </span>
          </template>
        </bk-input>
      </bk-form-item>
      <bk-form-item :label="$t('确认密码')" property="confirmPassword" required>
        <bk-input
          :class="{ 'is-error': isError }"
          :type="isConfirmPassword ? 'password' : 'text'"
          v-model="formData.confirmPassword"
          @input="changePassword">
          <template #suffix>
            <span class="copy-icon">
              <i class="user-icon icon-copy text-[#3A84FF] text-[14px] " @click="copy(formData.confirmPassword)" />
            </span>
            <span
              v-show="!isConfirmPassword"
              class="inline-flex text-[14px] ml-[8px] mr-[8px] text-[#c4c6cc] hover:text-[#313238]"
              @click="isConfirmPassword = true">
              <eye />
            </span>
          </template>
        </bk-input>
        <div class="bk-form-error" v-show="isError">{{ $t('两次输入的密码不一致，请重新输入') }}</div>
      </bk-form-item>
    </bk-form>
  </bk-dialog>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { Eye } from 'bkui-vue/lib/icon';
import { reactive, ref, watch } from 'vue';

import { logout } from '@/common/auth';
import { putPersonalCenterUserPassword } from '@/http';
import { t } from '@/language/index';
import { copy } from '@/utils';

const isOldPassword  = ref(false);
const isNewPassword  = ref(false);
const isConfirmPassword = ref(false);

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

const changePassword = () => {
  isError.value = false;
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
  position: absolute;
  top: 50%;
  right: 30px;
  transform: translate(0,  -50%)
}
</style>
