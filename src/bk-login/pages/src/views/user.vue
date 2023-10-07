<template>
  <div class="cursor-pointer" @click="goBack">&lt; 返回上一级</div>
  <h2 class="header">请选择你要登录的账号</h2>
  <div class="account">
    <div
      class="item"
      v-for="item in userList"
      :class="userId === item.id ? 'active' : ''"
      :key="item.id"
      @click="userId = item.id">
      {{ `${item.username}(${item.full_name})` }}
      <Done v-if="userId === item.id" class="check-icon" />
    </div>
  </div>
  <div>
    <bk-button
      theme="primary"
      size="large"
      style="width: 100%"
      :disabled="!userId"
      @click="handleLogin">
      立即登录
    </bk-button>
  </div>
</template>

<script setup lang="ts">
import { getUserList, signInByUser } from '@/http/api';
import { ref, onBeforeMount, type Ref } from 'vue';
import { useRouter } from 'vue-router';
import { Done } from 'bkui-vue/lib/icon';

interface User {
  id: string;
  username: string;
  full_name: string;
}

const router = useRouter();
const goBack = () => {
  router.push('/');
};

const userList: Ref<User[]> = ref([]);
const userId = ref('');

const handleLogin = () => {
  signInByUser({
    user_id: userId.value,
  }).then((res) => {
    window.location.href = res.redirect_uri;
  });
};

onBeforeMount(() => {
  getUserList().then((res) => {
    userList.value = res;
    // 如果只有一个账号，默认选中
    if (res.length === 1) {
      userId.value = res[0].id;
    }
  });
});
</script>

<style lang="postcss" scoped>
.cursor-pointer {
  cursor: pointer;
}
.header {
  width: 400px;
  height: 28px;
  font-size: 20px;
  color: #313238;
  line-height: 28px;
  margin: 16px 0 24px;
}
.account {
  margin-bottom: 40px;

  .item {
    position: relative;
    height: 40px;
    line-height: 40px;
    font-size: 16px;
    background: #F5F7FA;
    padding: 0 16px;
    cursor: pointer;
    margin-bottom: 8px;

    &.active {
      background: #E1ECFF;
    }

    &:hover {
      background: #F0F1F5;
    }

    .check-icon {
      position: absolute;
      font-size: 32px;
      right: 10px;
      top: 4px;
      color: #3A84FF;
    }
  }
}
</style>
