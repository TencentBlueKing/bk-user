<template>
  <div class="reset-wrapper">
    <div class="reset-box-content">
      <div class="reset-password-header">
        <p class="title">{{ $t('设置新密码') }}</p>
      </div>
      <bk-form ref="formRef" form-type="vertical" :model="formData" :rules="rules">
        <bk-form-item style="margin-bottom: 16px;" property="account" error-display-type="tooltips">
          <bk-select
            size="large"
            v-model="formData.account"
            :placeholder="$t('选择账号')"
            filterable
            @change="handleSelect"
          >
            <bk-option
              v-for="(item, index) in accounts"
              :id="item.tenant_user_id"
              :key="index"
              :name="item.display_name"
            />
          </bk-select>
        </bk-form-item>
        <bk-form-item style="margin-bottom: 16px;" property="password" error-display-type="tooltips">
          <bk-input
            :class="['password-input', { 'is-enter': isEnter }]"
            size="large"
            v-model="formData.password"
            :placeholder="$t('新密码')"
            type="password"
            @blur="handleBlur"
            @keypress="handleKeypress">
          </bk-input>
        </bk-form-item>
        <bk-form-item
          class="confirm-password"
          style="margin-bottom: 32px;"
          property="confirmPassword"
          error-display-type="tooltips">
          <bk-input
            :class="['password-input', { 'is-enter': isEnter }]"
            size="large"
            v-model="formData.confirmPassword"
            :placeholder="$t('确认新密码')"
            type="password"
            @input="changePassword"
            @blur="handleBlur"
            @keypress="handleKeypress">
          </bk-input>
          <bk-popover
            v-if="isError"
            :content="$t('两次输入的密码不一致，请重新输入')"
            placement="top"
          >
            <ExclamationCircleShape class="error-icon" />
          </bk-popover>
        </bk-form-item>
        <bk-form-item>
          <bk-button
            style="width: 100%;"
            theme="primary"
            size="large"
            :loading="loading"
            @click="handleResetPassword"
          >
            {{ $t('确定') }}
          </bk-button>
        </bk-form-item>
      </bk-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Message } from 'bkui-vue';
import { ExclamationCircleShape } from 'bkui-vue/lib/icon';
import { reactive, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import { logout } from '@/common/auth';
import { useValidate } from '@/hooks';
import { getUsers, resetPassword } from '@/http';
import { t } from '@/language/index';

const route = useRoute();
const validate = useValidate();

const formRef = ref();
const accounts = ref([]);
const formData = reactive({
  account: '',
  password: '',
  confirmPassword: '',
});

const rules = ref({
  account: [validate.required],
  password: [validate.required],
  confirmPassword: [validate.required],
});

watch(() => route.query.token, (val) => {
  if (val) {
    getUsers({ token: route.query.token }).then((res) => {
      accounts.value = res.data;
    })
      .catch((e) => {
        console.warn(e);
      });
  }
}, {
  immediate: true,
});

const handleSelect = (id) => {
  formData.account = id;
};

const isError = ref(false);
const isLoading = ref(false);

const changePassword = () => {
  isError.value = false;
};

const handleResetPassword = async () => {
  try {
    await formRef.value?.validate();
    if (formData.password !== formData.confirmPassword) {
      return isError.value = true;
    }
    isLoading.value = true;
    await resetPassword({
      tenant_user_id: formData.account,
      password: formData.password,
      token: route.query.token,
    });
    Message({ theme: 'success', message: t('修改密码成功') });
    logout();
  } catch (e) {
    console.warn(e);
  } finally {
    isLoading.value = false;
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

<style lang="less" scoped>
.reset-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #fafbfd;
}

.reset-box-content {
  position: absolute;
  inset: 0;
  width: 480px;
  height: 360px;
  padding: 40px 40px 32px;
  margin: auto;
  background: #FFF;
  border-radius: 10px;
  box-shadow: 0 4px 12px 0 #0003;

  .reset-password-header {
    color: #313238;

    .title {
      height: 42px;
      margin-bottom: 32px;
      font-size: 32px;
      font-weight: 700;
    }
  }

  ::v-deep .bk-form {
    .bk-input {
      border: none;

      span {
        background: #F0F1F5;
      }
    }

    input {
      background: #F0F1F5;
      border: none;
      border-radius: 2px;
    }

    .confirm-password {
      position: relative;

      .error-icon {
        position: absolute;
        top: 12px;
        right: 8px;
        font-size: 16px;
        color: #ea3636;
      }
    }
  }
}

::v-deep .bk-form-error-tips {
  top: 12px;
}

::v-deep .is-error {
  .password-input {
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
