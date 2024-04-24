<template>
  <div class="bg-white px-[12px] h-[52px] flex shadow-[0_3px_4px_0_#0000000a] pt-[10px] relative z-10">
    <bk-input
      v-model="search"
      type="search"
    ></bk-input>
    <div class="user-icon icon-refresh bg-[#F0F1F5] h-[32px] w-[32px] ml-[8px] !leading-[32px] cursor-pointer">
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const search = ref('');
</script>
