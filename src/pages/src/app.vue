<script setup lang="ts">
import {
  ref,
} from 'vue';
import { useUser } from '@/store/user';
import { getUser } from '@/http/api';
import { Message } from 'bkui-vue';
import HeaderBox from './views/Header.vue';

// 加载完用户数据才会展示页面
const isLoading = ref(false);
// 获取用户数据
const user = useUser();
getUser()
  .then((data) => {
    user.setUser(data);
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
