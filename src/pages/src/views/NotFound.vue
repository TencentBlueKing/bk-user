<template>
  <bk-exception
    v-bkloading="{
      opacity: 1,
      loading: isLoading,
    }"
    class="exception-wrap-item"
    type="404"
    :title="$t('页面不存在')"
  >
    <bk-button theme="primary" @click="handleRefresh">
      {{ $t('刷新页面') }}
    </bk-button>
    <bk-button theme="primary" @click="backHome">
      {{ $t('返回首页') }}
    </bk-button>
  </bk-exception>
</template>

<script setup lang="ts">
import { onBeforeMount, ref } from 'vue';

import router from '../router';

const isLoading = ref(false);
const handleRefresh = () => {
  window.location.reload();
};

const backHome = () => {
  router.push({ name: 'organization' });
};

onBeforeMount(() => {
  isLoading.value = true;
  setTimeout(() => {
    isLoading.value = false;
  }, 300);
});
</script>

<style lang="postcss" scoped>
.exception-wrap-item {
  margin: 100px auto;
}

.bk-button {
  margin-left: 8px;
}
</style>
