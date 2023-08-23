<script setup lang="ts">
import { AngleDownLine } from 'bkui-vue/lib/icon';
import { ref } from 'vue';

import { logout } from '@/common/auth';
import { useUser } from '@/store/user';

const user = useUser();
const userInfo = ref(user.user);
</script>

<template>
  <bk-popover
    class="user-home"
    placement="bottom-end"
    theme="light"
  >
    <span class="user-name">
      {{ userInfo.username }}
      <angle-down-line />
    </span>
    <template #content>
      <span
        class="logout"
        @click="logout"
      >退出</span>
    </template>
  </bk-popover>
</template>

<style lang="postcss" scoped>
.user-home {
  z-index: 1000;
  font-size: 14px;

  .user-name {
    cursor: pointer;
  }

  .logout {
    display: inline-block;
    width: 50px;
    text-align: center;
    cursor: pointer;
  }
}
</style>
