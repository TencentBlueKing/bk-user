<template>
  <bk-form form-type="vertical">
    <div class="logo">
      <img src="../../../static/images/user.svg" />
    </div>
    <bk-form-item>
      <div style="text-align: center;">
        <bk-button
          theme="primary"
          size="large"
          class="login-btn"
          @click="handleLogin">
          {{ $t('立即登录') }}
        </bk-button>
      </div>
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
    height: 170px;
  }
}
.login-btn {
  width: 140px;
  margin-top: 10px;
}
</style>
