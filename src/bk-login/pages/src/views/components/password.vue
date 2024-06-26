<template>
  <bk-form ref="formRef" form-type="vertical" :model="formData" :rules="rules">
    <bk-form-item property="username">
      <bk-input
        size="large"
        v-model="formData.username"
        :placeholder="isAdmin ? $t('请输入管理员账号') : $t('请输入用户名')"
      >
      </bk-input>
    </bk-form-item>

    <bk-form-item property="password">
      <bk-input
        size="large"
        v-model="formData.password"
        type="password"
        :placeholder="$t('请输入密码')"
        @enter="handleLogin">
      </bk-input>
    </bk-form-item>

    <p class="error-text" v-if="errorMessage">{{ errorMessage }}</p>

    <bk-form-item>
      <bk-button
        theme="primary"
        size="large"
        class="login-btn"
        :loading="loading"
        @click="handleLogin">
        {{ $t('立即登录') }}
      </bk-button>
    </bk-form-item>
  </bk-form>
</template>

<script setup lang="ts">
import { signInByPassword } from '@/http/api';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import useAppStore from '@/store/app';
import { t } from '@/language/index';

const appStore = useAppStore();

const props = defineProps({
  idpId: {
    type: String,
    default: '',
  },
  isAdmin: {
    type: Boolean,
    default: false,
  },
});

const router = useRouter();

const loading = ref(false);
const formRef = ref();
const formData = ref({
  username: '',
  password: '',
});
const rules = ref({
  username: [
    { required: true, message: t('请输入用户名'), trigger: 'blur' },
  ],
  password: [
    { required: true, message: t('请输入密码'), trigger: 'blur' },
  ],
});
const errorMessage = ref('');

const handleLogin = () => {
  errorMessage.value = '';
  formRef.value.validate().then(() => {
    loading.value = true;
    signInByPassword(
      appStore.tenantId,
      props.idpId,
      {
        username: formData.value.username,
        password: formData.value.password,
      },
    ).then(() => {
      window.location.href = `${window.SITE_URL}/page/users/`;
    })
      .catch((error) => {
        errorMessage.value = error?.message || t('登录失败');
      })
      .finally(() => {
        loading.value = false;
      });
  });
};

</script>

<style scoped lang="postcss">
.login-btn {
  width: 100%;
  margin-top: 10px;
}
.error-text {
  text-align: center;
  color: #ea3636;
}

</style>
