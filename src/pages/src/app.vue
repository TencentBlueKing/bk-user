<script setup lang="ts">
import { Message } from 'bkui-vue';
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import HeaderBox from './views/Header.vue';

import { currentUser } from '@/http';
import { t } from '@/language/index';
import { useUser } from '@/store';
import Password from '@/views/reset-password/index.vue';
import ResetPassword from '@/views/reset-password/newPassword.vue';

const route = useRoute();

const showName = ref(null);
// 判断是否是重置密码的路由
watch(() => route.name, (val) => {
  if (val === 'password' || val === 'resetPassword') {
    showName.value = val;
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
    <Password v-if="showName === 'password'" />
    <ResetPassword v-else-if="showName === 'resetPassword'" />
    <bk-loading
      v-else
      :loading="isLoading"
      :class="{
        'main-loading': isLoading
      }"
    >
      <HeaderBox v-if="!isLoading" />
    </bk-loading>
  </div>
</template>

<style lang="less" scoped>
  .main-loading {
    margin-top: 25vw;
  }
</style>
