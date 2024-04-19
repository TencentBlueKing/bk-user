<template>
  <bk-resize-layout
    class="h-[calc(100vh-52px)]"
    immediate
    :min="280"
    :max="400"
    :initial-divide="280">
    <template #aside>
      <Aside @updateOrg="handleUpdateOrg" />
    </template>
    <template #main>
      <section>
        <div class="text-[#313238] leading-[52px] px-[24px] text-[16px] shadow-[0_3px_4px_0_#0000000a] bg-white">
          {{ selected?.name }}
        </div>
      </section>
    </template>
  </bk-resize-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';

import Aside from './components/aside.vue';

const selected = ref({});

const handleUpdateOrg = (org: any) => {
  selected.value = org;
};
</script>

