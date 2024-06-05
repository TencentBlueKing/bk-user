<template>
  <div class="operation-wrapper">
    <bk-form
      class="operation-content"
      ref="formRef"
      form-type="vertical"
      :model="formData"
      :rules="rules">
      <Row :title="$t('基本信息')">
        <div class="flex justify-between">
          <div class="w-[424px]">
            <bk-form-item :label="$t('租户名称')" property="name" required>
              <bk-input v-model="formData.name" :placeholder="validate.name.message" @focus="handleChange" />
            </bk-form-item>
            <bk-form-item :label="$t('租户ID')" property="id" required>
              <bk-input
                v-model="formData.id"
                :placeholder="validate.id.message"
                :disabled="isEdit"
                @focus="handleChange" />
            </bk-form-item>
            <bk-form-item v-if="!isEdit" :label="$t('是否启用')" required>
              <bk-switcher
                :value="isEnabled"
                theme="primary"
                size="large"
                @change="changeStatus"
              />
            </bk-form-item>
          </div>
          <bk-upload
            class="mt-[26px]"
            theme="picture"
            with-credentials
            :multiple="false"
            :files="files"
            :handle-res-code="handleRes"
            :url="formData.logo"
            :custom-request="customRequest"
            :size="2"
            @delete="handleDelete"
            @error="handleError"
          />
        </div>
      </Row>
      <Row v-if="!isEdit" :title="$t('内置管理账号')">
        <bk-form-item :label="$t('用户名')" required>
          <bk-input
            :model-value="`${userStore.user.username}-${formData.id}`"
            disabled
          />
        </bk-form-item>
        <bk-form-item :label="$t('密码')" property="fixed_password" required>
          <div class="flex justify-between">
            <passwordInput
              v-model="formData.fixed_password"
              :value="formData.fixed_password"
              @change="changePassword" />
            <bk-button
              outline
              theme="primary"
              :class="['ml-[8px]', { 'min-w-[88px]': $i18n.locale === 'zh-cn' }]"
              @click="handleRandomPassword">
              {{ $t('随机生成') }}
            </bk-button>
          </div>
        </bk-form-item>
        <bk-form-item :label="$t('通知方式')">
          <span class="inline-flex items-center text-sm pb-[8px] mb-[8px]" :class="[isClickEmail ? 'active-tab' : '']">
            <bk-checkbox v-model="emailValue" :before-change="beforeEmailChange" @change="changeEmail" />
            <span
              class="ml-[6px] cursor-pointer text-[#63656E]"
              @click="emailClick"
            >
              {{ $t('邮箱') }}
            </span>
          </span>
          <span
            class="inline-flex items-center ml-[24px] text-sm pb-[8px] mb-[8px]"
            :class="[isClickEmail ? '' : 'active-tab']">
            <bk-checkbox v-model="smsValue" :before-change="beforeTelChange" @change="changeSms" />
            <span
              class="ml-[6px] cursor-pointer text-[#63656E]"
              @click="phoneClick"
            >
              {{ $t('短信') }}
            </span>
          </span>
          <div v-if="isClickEmail">
            <bk-input
              :class="{ 'input-error': emailError }"
              v-model="formData.email"
              @focus="handleChange"
              @blur="emailBlur"
              @input="handleInput" />
            <p class="error" v-show="emailError">{{ $t('请输入正确的邮箱地址') }}</p>
          </div>
          <PhoneInput
            v-else
            :form-data="formData"
            :tel-error="telError"
            :required="smsValue"
            @change-country-code="changeCountryCode"
            @change-tel-error="changeTelError" />
        </bk-form-item>
      </Row>
    </bk-form>
    <div class="footer">
      <bk-button theme="primary" @click="handleSubmit" :loading="state.isLoading" :disabled="isEdit && isDisabled">
        {{ $t('提交') }}
      </bk-button>
      <bk-button @click="() => $emit('handleCancelEdit')">
        {{ $t('取消') }}
      </bk-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { computed, defineEmits, defineProps, reactive, ref, watch } from 'vue';

import Row from '@/components/layouts/row.vue';
import passwordInput from '@/components/passwordInput.vue';
import PhoneInput from '@/components/phoneInput.vue';
import { useAdminPassword, useValidate } from '@/hooks';
import { createTenants, putTenants } from '@/http';
import { t } from '@/language/index';
import { useUser } from '@/store';
import { getBase64 } from '@/utils';

const userStore = useUser();

const props = defineProps({
  tenantsData: {
    type: Object,
    default: {},
  },
  type: {
    type: String,
    default: '',
  },
});

const emit = defineEmits(['updateTenantsList', 'handleCancelEdit']);

const validate = useValidate();

const formRef = ref();
const formData = reactive({
  ...props.tenantsData,
});

watch(() => [formData.name, formData.logo], (val) => {
  isDisabled.value = isEdit.value ? (props.tenantsData.name === val[0] && props.tenantsData.logo === val[1]) : false;
});

const isEnabled = ref(props.tenantsData.status === 'enabled');
const changeStatus = () => {
  isEnabled.value = !isEnabled.value;
};

const state = reactive({
  count: 0,
  list: [],
  isLoading: false,
});

const rules = {
  name: [validate.required, validate.name],
  id: [validate.required, validate.id],
  fixed_password: [validate.required],
};

const isEdit = computed(() => props.type === 'edit');

// 上传头像
const files = computed(() => {
  const img = [];
  if (formData.logo !== '') {
    img.push({
      url: formData.logo,
    });
    return img;
  }
  return [];
});

const handleRes = (response: any) => {
  if (response.id) {
    return true;
  }
  return false;
};

const customRequest = (event) => {
  getBase64(event.file).then((res) => {
    formData.logo = res;
  })
    .catch((e) => {
      console.warn(e);
    });
  handleChange();
};

const handleDelete = () => {
  formData.logo = '';
  handleChange();
};

const handleError = (file) => {
  if (file.size > (2 * 1024 * 1024)) {
    Message({ theme: 'error', message: t('图片大小超出限制，请重新上传') });
  }
};

// 校验表单
async function handleSubmit() {
  await formRef.value.validate();

  if (props.type === 'add') {
    if (emailValue.value) {
      handleBlur();
    } else if (smsValue.value && formData.phone === '') {
      changeTelError(true);
    }
  }

  if (emailError.value || telError.value) return;

  state.isLoading = true;
  props.type === 'add' ? createTenantsFn() : putTenantsFn();
}

// 新建租户
function createTenantsFn() {
  formData.status = isEnabled.value ? 'enabled' : 'disabled';
  formData.notification_methods = [];
  if (emailValue.value) formData.notification_methods.push('email');
  if (smsValue.value) formData.notification_methods.push('sms');
  createTenants(formData).then(() => {
    emit('updateTenantsList', 'add', formData.id);
  })
    .finally(() => {
      state.isLoading = false;
    });
}
// 更新租户
function putTenantsFn() {
  const params = {
    name: formData.name,
    logo: formData.logo,
  };

  putTenants(formData.id, params).then(() => {
    emit('updateTenantsList', 'edit');
  })
    .finally(() => {
      state.isLoading = false;
    });
}

const handleChange = () => {
  window.changeInput = true;
};

const {
  changePassword,
  handleRandomPassword,
  emailError,
  telError,
  isEmail,
  handleBlur,
  handleInput,
  changeCountryCode,
  changeTelError,
} = useAdminPassword(formData);

const isClickEmail = ref(true);
const emailValue = ref(true);
const smsValue = ref(false);
const isDisabled = ref(true);

// 点击电话之前的校验
const  beforeTelChange = () => {
  if (emailValue.value) {
    if (formData.email && !emailError.value) {
      isClickEmail.value = false;
      return true;
    }
    handleBlur();
    return false;
  }
  isClickEmail.value = false;
  return true;;
};

// 点击邮箱之前的校验
const  beforeEmailChange = () => {
  if (smsValue.value) {
    if (formData.phone && !telError.value) {
      isClickEmail.value = true;
      return true;
    }
    changeTelError(true);
    return false;
  }
  isClickEmail.value = true;
  return true;;
};

const emailClick = () => {
  if (smsValue.value) {
    if (formData.phone && !telError.value) {
      isClickEmail.value = true;
    } else {
      changeTelError(true);
    }
  } else {
    isClickEmail.value = true;
  }
};

const phoneClick = () => {
  if (emailValue.value) {
    if (formData.email && !emailError.value) {
      isClickEmail.value = false;
    } else {
      handleBlur();
    }
  } else {
    isClickEmail.value = false;
  }
};

const changeSms = () => {
  telError.value = smsValue.value ? telError.value : false;
};
const changeEmail = () => {
  emailError.value = emailValue.value ? emailError.value : false;
};

const emailBlur = () => {
  emailValue.value && handleBlur();
};
</script>

<style lang="less" scoped>
.operation-wrapper {
  padding: 20px 24px;

  .footer {
    .bk-button {
      min-width: 88px;
      margin-right: 8px;
    }
  }
}

.error {
  position: absolute;
  left: 0;
  padding-top: 4px;
  font-size: 12px;
  line-height: 1;
  color: #ea3636;
  text-align: left;
  animation: form-error-appear-animation 0.15s;
}

.input-error {
  border-color: #ea3636 !important;
}

::v-deep .bk-upload-trigger--picture {
  margin: 0 -4px 8px 0;
}
.active-tab {
  border-bottom: 2px solid #3A84FF;
}
</style>
