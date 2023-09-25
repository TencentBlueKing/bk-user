<template>
  <bk-form ref="formRef" form-type="vertical" :rules="rules" :model="formData">
    <bk-form-item property="username">
      <bk-input size="large" v-model="formData.username" placeholder="请输入用户名"></bk-input>
    </bk-form-item>

    <bk-form-item property="password">
      <bk-input size="large" v-model="formData.password" type="password" placeholder="请输入密码"></bk-input>
    </bk-form-item>

    <bk-form-item>
      <bk-button
        theme="primary"
        size="large"
        class="login-btn"
        :loading="loading"
        @click="handleLogin">
        立即登录
      </bk-button>
    </bk-form-item>
  </bk-form>
</template>

<script setup lang="ts">
import { signInByPassword } from '@/http/api';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  idpId: {
    type: String,
    default: '',
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
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
  ],
});

const handleLogin = () => {
  console.log('login');
  formRef.value.validate().then(() => {
    loading.value = true;
    signInByPassword(
      props.idpId,
      {
        username: formData.value.username,
        password: formData.value.password,
      },
    ).then(() => {
      loading.value = false;
      router.push('/users');
    });
  });
};

</script>

<style scoped lang="less">
.login-btn {
  width: 100%;
  margin-top: 10px;
}

</style>
