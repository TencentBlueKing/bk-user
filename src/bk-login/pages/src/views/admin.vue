<template>
  <div style="margin-top: -28px">
    <bk-link class="back" @click.prevent="handleBack">&lt; 返回上一级</bk-link>
    <h1 class="title">管理员登录</h1>
    <span class="desc">可使用内置管理员账号进行登录</span>
    <Password is-admin :idp-id="appStore.manageIdpId"></Password>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import Password from './components/password.vue';
import useAppStore from '@/store/app';

const appStore = useAppStore();
const router = useRouter();

const handleBack = () => {
  // router.push({ name: 'login-plain' });
  router.back();
};
</script>

<style lang="postcss" scoped>
.back {
  display: inline-block;
  font-size: 14px;
  padding-bottom: 16px;
}
.title {
  font-size: 24px;
  font-weight: bold;
  color: #313238;
  margin-bottom: 12px;
}
.desc {
  display: inline-block;
  font-size: 14px;
  color: #63656E;
  margin-bottom: 24px;
}
</style>
