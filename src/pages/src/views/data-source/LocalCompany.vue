<template>
  <bk-tab
    v-model:active="active"
    type="unborder-card"
    ext-cls="tab-details"
    @change="handleChange"
  >
    <bk-tab-panel
      v-for="item in panels"
      :key="item.name"
      :name="item.name"
      :label="item.label"
    >
      <RouterView />
    </bk-tab-panel>
  </bk-tab>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRoute } from 'vue-router';

import { t } from '@/language/index';
import router from '@/router/index';

const route = useRoute();
const active = ref(route.name);
const panels = reactive([
  { name: 'local', label: t('本租户') },
  { name: 'other', label: t('其他租户') },
]);

const handleChange = (name) => {
  router.push({ name });
};
</script>

<style lang="less" scoped>
@import url("@/css/tabStyle.less");
</style>
