<template>
  <bk-dialog
    :is-show="isShow"
    :title="$t('重置密码')"
    theme="primary"
    size="normal"
    :height="200"
    @closed="handleClose"
  >
    <bk-loading :loading="loading">
      <bk-form
        form-type="vertical"
        ref="formRef"
        :model="formData"
        :rules="passwordRules"
      >
        <bk-form-item
          :label="$t('新密码')"
          property="password"
          required
        >
          <div class="flex items-center">
            <passwordInput
              v-model="formData.password"
              v-bk-tooltips="{
                content: passwordTips.join('\n'),
                theme: 'light',
                disabled: !showPasswordTips,
              }"
              clearable
              :style="{ width: '80%' }"
              :placeholder="showPasswordTips ? passwordTips.join('、') : $t('请输入新密码')"
            />
            <bk-button
              outline
              theme="primary"
              class="ml-[8px]"
              @click="handleRandomPassword"
            >
              {{$t('随机生成')}}
            </bk-button>
          </div>
        </bk-form-item>
        <bk-form-item
          :label="$t('确认密码')"
          property="confirmPassword"
          required
        >
          <passwordInput
            v-model="formData.confirmPassword"
            :placeholder="$t('请再次输入密码')"
          />
        </bk-form-item>
      </bk-form>
    </bk-loading>
    <template #footer>
      <div class="flex justify-end">
        <bk-button
          class="mr-[8px]"
          @click="handleCancel"
        >
          {{$t('取消')}}
        </bk-button>
        <bk-button
          theme="primary"
          @click="handleConfirm"
        >
          {{$t('确定')}}
        </bk-button>
      </div>
    </template>
  </bk-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import passwordInput from './passwordInput.vue';

import { randomPasswords } from '@/http';

interface Props {
  isShow: boolean;
  loading?: boolean;
  passwordTips?: string[];
  showPasswordTips?: boolean;
  dataSourceId?: string;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  passwordTips: () => [],
  showPasswordTips: true,
});

const emits = defineEmits<{
  'update:isShow': [value: boolean];
  'confirm': [password: string];
  'cancel': [];
}>();

const { t } = useI18n();

const formRef = ref();
const formData = reactive({
  password: '',
  confirmPassword: '',
});

const passwordRules = {
  password: [{ required: true, message: t('新密码不能为空'), trigger: 'blur' }],
  confirmPassword: [
    { required: true, message: t('确认密码不能为空'), trigger: 'blur' },
    {
      validator: (value: string) => value === formData.password,
      message: t('两次输入的密码不一致,请重新输入'),
      trigger: 'blur',
    },
  ],
};

// 监听弹窗关闭，清理表单
watch(() => props.isShow, (newVal) => {
  if (!newVal) {
    formData.password = '';
    formData.confirmPassword = '';
    formRef.value?.clearValidate();
  }
});

// 随机生成密码
const handleRandomPassword = async () => {
  if (!props.dataSourceId) {
    console.warn('dataSourceId is required for random password generation');
    return;
  }
  try {
    const res = await randomPasswords({ data_source_id: props.dataSourceId });
    formData.password = res.data?.password || '';
  } catch (e) {
    console.warn(e);
  }
};

// 确认
const handleConfirm = async () => {
  try {
    await formRef.value.validate();
    emits('confirm', formData.password);
  } catch (e) {
    console.warn(e);
  }
};

// 取消
const handleCancel = () => {
  emits('update:isShow', false);
  emits('cancel');
};

// 关闭
const handleClose = () => {
  emits('update:isShow', false);
};
</script>
