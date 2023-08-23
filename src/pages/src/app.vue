<script setup lang="ts">
import { Message } from 'bkui-vue';
import {
  ref,
} from 'vue';

import HeaderBox from './views/Header.vue';

import { currentUser } from '@/http/api';
import { useUser } from '@/store/user';

// 加载完用户数据才会展示页面
const isLoading = ref(false);
// 获取用户数据
const user = useUser();
currentUser()
  .then((res) => {
    user.setUser(res.data);
    isLoading.value = false;
  })
  .catch(() => {
    Message('获取用户信息失败，请检查后再试');
  });
</script>

<template>
  <bk-loading
    :loading="isLoading"
    :class="{
      'main-loading': isLoading
    }"
  >
    <HeaderBox v-if="!isLoading" />
  </bk-loading>
</template>

<style lang="less" scoped>
  .main-loading {
    margin-top: 25vw;
  }
</style>
