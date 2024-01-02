<template>
  <bk-exception
    class="exception-wrap-item"
    type="404"
    title="页面不存在"
  >
    <bk-button theme="primary" @click="handleRefresh">
      刷新页面
    </bk-button>
    <bk-button theme="primary" @click="backHome">
      返回首页
    </bk-button>
  </bk-exception>
</template>

<script setup lang="ts">
import router from '../router';

const handleRefresh = () => {
  window.location.reload();
};

const backHome = () => {
  router.push({ name: 'organization' });
};
</script>

<style lang="postcss" scoped>
.exception-wrap-item {
  margin: 100px auto;
}

.bk-button {
  margin-left: 8px;
}
</style>
