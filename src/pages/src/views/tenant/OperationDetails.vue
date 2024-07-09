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
          <div class="w-[424px] mr-[28px]">
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
            :tip="$t('支持 jpg、png，尺寸不大于 1024px*1024px，不大于 256KB')"
          />
        </div>
      </Row>
      <Row v-if="!isEdit" :title="$t('内置管理账号')">
        <bk-form-item :label="$t('用户名')" required>
          <bk-input
            :model-value="userStore.user.username"
            disabled
          />
        </bk-form-item>
        <bk-form-item :label="$t('密码')" property="fixed_password" required>
          <div class="flex justify-between">
            <passwordInput
              v-model="formData.fixed_password"
              @change="changePassword"
              @input="inputPassword" />
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
          <div class="mb-[18px]">
            <bk-checkbox v-model="smsValue" @change="changeSms">{{ $t('短信') }}</bk-checkbox>
            <PhoneInput
            :form-data="formData"
            :tel-error="telError"
            :required="smsValue"
            @change-country-code="changeCountryCode"
            @change-tel-error="changeTelError" />
          </div>
          <div>
            <bk-checkbox v-model="emailValue"  @change="changeEmail">{{ $t('邮箱') }}</bk-checkbox>
            <bk-input
              :class="{ 'input-error': emailError }"
              v-model="formData.email"
              @focus="handleChange"
              @blur="emailBlur"
              @input="handleInput" />
            <p class="error" v-show="emailError">{{ $t('请输入正确的邮箱地址') }}</p>
          </div>
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
  if (props.type === 'add') {
    if (emailValue.value) handleBlur();
    if (smsValue.value && !formData.phone) changeTelError(true);
}
  await formRef.value.validate();

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
    emit('updateTenantsList', 'add', formData);
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

const inputPassword = (val) => {
  formData.fixed_password = val;
};

const emailValue = ref(true);
const smsValue = ref(false);
const isDisabled = ref(true);


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
::v-deep .bk-upload__tip {
  width: 0;
  color: #999
}
</style>
