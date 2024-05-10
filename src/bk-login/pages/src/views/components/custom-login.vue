<template>
  <bk-form form-type="vertical">
    <div class="logo">
      <img src="../../../static/images/user.png" />
    </div>
    <bk-form-item>
      <bk-button
        theme="primary"
        size="large"
        class="login-btn"
        @click="handleLogin">
        立即登录
      </bk-button>
    </bk-form-item>
  </bk-form>
</template>

<script setup lang="ts">
import useAppStore from '@/store/app';
const props = defineProps({
  idpId: {
    type: String,
    default: '',
  },
});

const appStore = useAppStore();
const handleLogin = () => {
  window.location.href = `${window.SITE_URL}/tenants/${appStore.tenantId}/idps/${props.idpId}/actions/login/`;
};
</script>

<style scoped lang="postcss">
.logo {
  text-align: center;
  img {
    height: 123px;
  }
}
.login-btn {
  width: 100%;
  margin-top: 10px;
}
</style>
