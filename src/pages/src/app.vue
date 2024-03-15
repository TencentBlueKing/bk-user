<script setup lang="ts">
import { Message } from 'bkui-vue';
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import HeaderBox from './views/Header.vue';

import { currentUser } from '@/http/api';
import { t } from '@/language/index';
import { useUser } from '@/store/user';
import ResetPassword from '@/views/reset-password/index.vue';

const route = useRoute();

const showPassword = ref(false);
// 判断是否是重置密码的路由
watch(() => route.name, (val) => {
  if (val === 'password' || val === 'resetPassword') {
    showPassword.value = true;
  } else {
    initUser();
  }
});

// 加载完用户数据才会展示页面
const isLoading = ref(false);
// 获取用户数据
const user = useUser();

const initUser = async () => {
  isLoading.value = true;
  currentUser()
    .then((res) => {
      user.setUser(res.data);
    })
    .catch(() => {
      Message(t('获取用户信息失败，请检查后再试'));
    })
    .finally(() => {
      isLoading.value = false;
    });
};
</script>

<template>
  <div>
    <bk-loading
      v-if="!showPassword"
      :loading="isLoading"
      :class="{
        'main-loading': isLoading
      }"
    >
      <HeaderBox v-if="!isLoading" />
    </bk-loading>
    <ResetPassword v-else />
  </div>
</template>

<style lang="less" scoped>
  .main-loading {
    margin-top: 25vw;
  }
</style>
